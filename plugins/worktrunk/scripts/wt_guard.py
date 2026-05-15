#!/usr/bin/env python3

import json
import os
import shutil
import shlex
import subprocess
import sys
from pathlib import Path


def load_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def response_continue() -> None:
    print(json.dumps({"continue": True}))


def response_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def run_git(cwd: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def git_ok(cwd: Path, args: list[str]) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return result.returncode == 0


def repo_context(cwd: Path) -> dict[str, str] | None:
    top = run_git(cwd, ["rev-parse", "--show-toplevel"])
    git_dir = run_git(cwd, ["rev-parse", "--path-format=absolute", "--git-dir"])
    common_dir = run_git(cwd, ["rev-parse", "--path-format=absolute", "--git-common-dir"])
    if not top or not git_dir or not common_dir:
        return None

    default_branch = run_git(
        cwd, ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"]
    )
    if default_branch and default_branch.startswith("origin/"):
        default_branch = default_branch.removeprefix("origin/")
    if not default_branch:
        default_branch = "main"

    return {
        "top": top,
        "git_dir": git_dir,
        "common_dir": common_dir,
        "default_branch": default_branch,
    }


def is_primary_worktree(ctx: dict[str, str]) -> bool:
    top = Path(ctx["top"])
    git_dir = Path(ctx["git_dir"])
    common_dir = Path(ctx["common_dir"])
    return git_dir == common_dir and (top / ".git").is_dir()


def normalize_branch_name(target: str) -> str:
    for prefix in ("refs/heads/", "origin/"):
        if target.startswith(prefix):
            return target.removeprefix(prefix)
    return target


def branch_ref_exists(cwd: Path, target: str) -> bool:
    normalized = normalize_branch_name(target)
    refs = [
        f"refs/heads/{normalized}",
        f"refs/remotes/origin/{normalized}",
    ]
    return any(git_ok(cwd, ["rev-parse", "--verify", "--quiet", ref]) for ref in refs)


def parse_git_invocations(command: str, default_cwd: Path) -> list[tuple[Path, str, list[str]]]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return []

    invocations: list[tuple[Path, str, list[str]]] = []
    separators = {";", "&&", "||", "|"}
    i = 0
    while i < len(tokens):
        if tokens[i] != "git":
            i += 1
            continue

        cwd = default_cwd
        i += 1
        while i < len(tokens):
            token = tokens[i]
            if token in separators:
                break
            if token == "-C" and i + 1 < len(tokens):
                cwd = Path(tokens[i + 1])
                i += 2
                continue
            if token.startswith("-C") and len(token) > 2:
                cwd = Path(token[2:])
                i += 1
                continue
            if token.startswith("-"):
                i += 1
                continue
            subcommand = token
            i += 1
            args: list[str] = []
            while i < len(tokens) and tokens[i] not in separators:
                args.append(tokens[i])
                i += 1
            invocations.append((cwd, subcommand, args))
            break
    return invocations


def switch_target(args: list[str]) -> str | None:
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            return args[i + 1] if i + 1 < len(args) else None
        if arg in ("-c", "-C", "--create"):
            return args[i + 1] if i + 1 < len(args) else "<new-branch>"
        if arg.startswith("--"):
            i += 1
            continue
        if arg.startswith("-") and arg != "-":
            i += 1
            continue
        return arg
    return None


def checkout_target(cwd: Path, args: list[str]) -> str | None:
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            return None
        if arg in ("-b", "-B", "--orphan"):
            return args[i + 1] if i + 1 < len(args) else "<new-branch>"
        if arg.startswith("-") and arg != "-":
            i += 1
            continue
        if branch_ref_exists(cwd, arg) or arg == "-":
            return arg
        return None
    return None


def blocks_primary_branch_switch(command: str, cwd: Path) -> str | None:
    for git_cwd, subcommand, args in parse_git_invocations(command, cwd):
        ctx = repo_context(git_cwd)
        if not ctx or not is_primary_worktree(ctx):
            continue

        default_branch = ctx["default_branch"]
        target = None
        if subcommand == "switch":
            target = switch_target(args)
        elif subcommand == "checkout":
            target = checkout_target(git_cwd, args)

        if not target:
            continue
        if target == "-":
            return (
                "Do not use `git switch -` or `git checkout -` from a primary "
                "worktree; keep the root checkout on its default branch and use "
                "`wt switch <branch>` for branch work."
            )

        normalized = normalize_branch_name(target)
        if normalized != default_branch:
            return (
                f"Do not switch primary worktree {ctx['top']} from "
                f"`{default_branch}` to `{target}`. Keep root checkouts on their "
                "default branch and use `wt switch <branch>` or "
                "`wt switch --create <branch>` for branch work."
            )
    return None


def main() -> int:
    payload = load_payload()
    tool_input = payload.get("tool_input", {})
    command = (
        tool_input.get("command")
        if isinstance(tool_input, dict)
        else None
    )
    if not isinstance(command, str) or shutil.which("wt") is None:
        response_continue()
        return 0

    if "git worktree add" in command:
        response_block(
            "Use `wt switch --create <branch>` instead of `git worktree add`; WorkTrunk applies its path template, hooks, and branch lifecycle management."
        )
        return 0

    if "git worktree remove" in command:
        response_block(
            "Use `wt remove <branch-or-path>` instead of `git worktree remove`; WorkTrunk keeps its state and worktree bookkeeping in sync."
        )
        return 0

    cwd_value = payload.get("cwd")
    if isinstance(tool_input, dict) and isinstance(tool_input.get("cwd"), str):
        cwd_value = tool_input["cwd"]
    cwd = Path(cwd_value) if isinstance(cwd_value, str) else Path(os.getcwd())
    reason = blocks_primary_branch_switch(command, cwd)
    if reason:
        response_block(reason)
        return 0

    response_continue()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
