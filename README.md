# WorkTrunk for Codex

Codex plugin bundle for [`wt`](https://worktrunk.dev): repo-local WorkTrunk skills, branch activity markers, and guardrails that keep Codex on `wt` instead of raw `git worktree`.

## What it adds

- Synced WorkTrunk reference docs inside a Codex skill
- Codex hooks that set `wt` branch markers:
  - `🤖` while Codex is working
  - `💬` when Codex is waiting for the next prompt
- A Bash guard hook that blocks `git worktree add/remove` and tells Codex to use `wt`
- Codex command docs for common WorkTrunk flows
- Agent handoff guidance for launching Codex, Goose, or another agent through `wt switch -x`, with `gh-dash`, `gh-enhance`, lazygit, and Neovim treated as optional human-facing entrypoints

## Install

Add the marketplace:

```bash
codex plugin marketplace add adrianmross/worktrunk-codex
```

Or from a local checkout:

```bash
codex plugin marketplace add /mnt/data/dev/adrianmross/worktrunk-codex
```

Or sync the current checkout directly into Codex's local plugin cache:

```bash
./scripts/install-local.sh
```

Enable the plugin in `~/.codex/config.toml`:

```toml
[features]
plugins = true

[plugins."worktrunk@worktrunk-codex"]
enabled = true
```

## Requirements

- `wt` on `PATH`
- `git` on `PATH`
- `jq` if you use the bundled Codex commit-generation example

## Notes

- This repo vendors WorkTrunk reference docs from `max-sixty/worktrunk` under `MIT OR Apache-2.0`.
- Codex does not expose Claude-style worktree lifecycle hooks, so this plugin enforces `wt` through a Bash guard hook plus skills and commands.

## Agent Handoff

For agent-native task starts, use WorkTrunk's execute path instead of driving a TUI:

```bash
wt switch pr:123 -x codex
wt switch --create fix-login --base=@ -x codex -- "Fix the login regression"
wt switch pr:123 -x goose
```

The bundled skill documents this in `skills/worktrunk/reference/agent-handoff.md`, and the `start-agent-task` command prompt gives Codex a concise workflow for PR, branch, and stacked-task handoffs.

## Linked Worktree Git Writes

Codex's default `workspace-write` sandbox keeps `.git` and the resolved `gitdir:` target read-only. In a linked git worktree, git writes land in the shared common git dir, so commands like `git commit`, `git branch -m`, and `git worktree lock` can fail even when the worktree itself is writable.

Use a dedicated profile for linked worktrees:

```toml
[profiles.worktree-git]
model = "oca/gpt-5-codex"
model_provider = "oca_responses"
approval_policy = "on-request"
model_reasoning_effort = "medium"
sandbox_mode = "danger-full-access"
```

Then launch Codex through a worktree-aware shell wrapper:

```zsh
codex_is_linked_worktree() {
  command -v git >/dev/null 2>&1 || return 1
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1

  local -a git_paths
  git_paths=("${(@f)$(git rev-parse --path-format=absolute --git-dir --git-common-dir 2>/dev/null)}")

  [[ ${#git_paths[@]} -ge 2 ]] || return 1
  [[ -n "${git_paths[1]}" && -n "${git_paths[2]}" ]] || return 1
  [[ "${git_paths[1]}" != "${git_paths[2]}" ]]
}

codex() {
  if codex_is_linked_worktree; then
    command codex -p worktree-git "$@"
    return $?
  fi

  command codex "$@"
}
```

If you do not want an automatic wrapper, the manual fallback is:

```bash
codex -p worktree-git
```
