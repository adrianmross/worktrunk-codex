#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

MARKERS = {
    "SessionStart": "💬",
    "UserPromptSubmit": "🤖",
    "Stop": "💬",
}


def state_dir() -> Path:
    root = os.environ.get("XDG_STATE_HOME")
    if root:
        return Path(root) / "worktrunk-codex"
    return Path.home() / ".local" / "state" / "worktrunk-codex"


def load_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def git_branch(cwd: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    branch = result.stdout.strip()
    if not branch or branch == "HEAD":
        return None
    return branch


def write_session_state(payload: dict, branch: str, marker: str) -> None:
    target = state_dir() / "sessions"
    target.mkdir(parents=True, exist_ok=True)
    session_id = payload.get("session_id") or "unknown"
    record = {
        "session_id": session_id,
        "branch": branch,
        "marker": marker,
        "updated_at": int(time.time()),
        "cwd": payload.get("cwd"),
        "hook_event_name": payload.get("hook_event_name"),
    }
    (target / f"{session_id}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    cutoff = time.time() - 7 * 24 * 60 * 60
    for path in target.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            continue


def set_marker(cwd: str, branch: str, marker: str) -> None:
    if shutil.which("wt") is None:
        return
    try:
        subprocess.run(
            ["wt", "config", "state", "marker", "set", marker, "--branch", branch],
            cwd=cwd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return


def main() -> int:
    payload = load_payload()
    event_name = payload.get("hook_event_name")
    marker = MARKERS.get(event_name)
    cwd = payload.get("cwd")
    if not marker or not cwd:
        print(json.dumps({"continue": True}))
        return 0

    branch = git_branch(cwd)
    if not branch:
        print(json.dumps({"continue": True}))
        return 0

    write_session_state(payload, branch, marker)
    set_marker(cwd, branch, marker)
    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
