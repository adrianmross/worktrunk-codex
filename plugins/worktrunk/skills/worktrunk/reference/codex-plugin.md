# Codex Plugin

This reference describes the Codex-specific WorkTrunk plugin behavior in this repository.

## Features

1. **Skill bundle** — Codex gets the upstream WorkTrunk docs locally under `skills/worktrunk/reference/`
2. **Activity markers** — Codex hooks set `wt` markers on the current branch:
   - `🤖` while Codex is working on a prompt
   - `💬` when Codex is idle and waiting for the next prompt
3. **Worktree guardrail** — a Bash `PreToolUse` hook blocks raw `git worktree add/remove`

## Marker behavior

The plugin maps Codex hook events to WorkTrunk markers:

- `SessionStart` -> `💬`
- `UserPromptSubmit` -> `🤖`
- `Stop` -> `💬`

Markers are written with:

```bash
wt config state marker set <marker> --branch <branch>
```

## Limitation

Codex currently exposes generic hook events (`SessionStart`, `UserPromptSubmit`, `Stop`, `PreToolUse`, `PostToolUse`) rather than Claude-style worktree lifecycle hooks.

That means this plugin can:

- steer Codex away from raw `git worktree` commands
- provide repo-local WorkTrunk guidance
- track branch activity

But it cannot:

- intercept a dedicated "create isolated worktree" event from Codex
- automatically clear markers on a guaranteed session-end event

If a marker survives after a Codex terminal closes, clear it manually:

```bash
wt config state marker clear
```

## Recommended Codex config

Enable plugins and this marketplace plugin in `~/.codex/config.toml`:

```toml
[features]
plugins = true

[plugins."worktrunk@worktrunk-codex"]
enabled = true
```

## Recommended user prompts

- "Create a new wt worktree for this task"
- "Set up WorkTrunk hooks for this repo"
- "Fix my wt shell integration"
- "Configure WorkTrunk commit generation for Codex"
