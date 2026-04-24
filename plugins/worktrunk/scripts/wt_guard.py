#!/usr/bin/env python3

import json
import shutil
import sys


def load_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def main() -> int:
    payload = load_payload()
    command = (
        payload.get("tool_input", {}).get("command")
        if isinstance(payload.get("tool_input"), dict)
        else None
    )
    if not isinstance(command, str) or shutil.which("wt") is None:
        print(json.dumps({"continue": True}))
        return 0

    if "git worktree add" in command:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Use `wt switch --create <branch>` instead of `git worktree add`; WorkTrunk applies its path template, hooks, and branch lifecycle management.",
                }
            )
        )
        return 0

    if "git worktree remove" in command:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Use `wt remove <branch-or-path>` instead of `git worktree remove`; WorkTrunk keeps its state and worktree bookkeeping in sync.",
                }
            )
        )
        return 0

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
