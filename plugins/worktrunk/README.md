# WorkTrunk Codex Plugin

Codex plugin for WorkTrunk.

## Included surfaces

- `skills/worktrunk/` — upstream WorkTrunk references plus Codex-specific guidance
- `hooks.json` — activity markers and `git worktree` guardrail
- `commands/` — common WorkTrunk workflow prompts for Codex
- `skills/worktrunk/reference/agent-handoff.md` — agent-native handoff patterns for `wt`, `gh`, Codex, Goose, gh-dash, gh-enhance, lazygit, and Neovim

## Hook behavior

- `SessionStart` -> `💬`
- `UserPromptSubmit` -> `🤖`
- `Stop` -> `💬`
- `PreToolUse` for `Bash` blocks raw `git worktree add/remove`

## Limitation

Codex does not currently expose dedicated worktree lifecycle hooks, so this plugin cannot rewrite agent-created worktrees the way Claude Code can. It compensates with skills, commands, and a Bash pre-tool guard.
