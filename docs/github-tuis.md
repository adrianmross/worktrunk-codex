# GitHub TUI Flow

This repo treats terminal UIs as human-facing entrypoints around the same command-line state agents can use directly.

## Responsibilities

- `gh`: scriptable GitHub state for agents.
- `gh-dash`: PR inbox, review queue, notifications, and triage.
- `gh-enhance`: GitHub Actions and checks TUI.
- `lazygit`: local git shaping, worktree visibility, stashes, rebases, commits, and branch cleanup.
- Neovim Diffview and Octo: human code review, line comments, PR metadata, and final inspection.
- `wt`: worktree lifecycle for both humans and agents.

Agents should prefer `gh`, `git`, and `wt` commands. Humans can use the TUIs to choose context and then launch the same `wt` commands.

## Suggested Human Flow

1. Use `gh-dash` to find the PR or notification.
2. Launch a worktree or agent task from the selected PR:

   ```bash
   wt switch pr:<number>
   wt switch pr:<number> -x codex
   ```

3. Use `gh-enhance` when you want an interactive checks view.
4. Use `lazygit` to shape commits locally.
5. Use Diffview and Octo for review comments and final code inspection.

## Suggested Agent Flow

Use scriptable commands instead of opening TUIs:

```bash
gh pr view <number> --json number,title,headRefName,baseRefName,author,url,reviewDecision
gh pr checks <number>
gh run list --limit 10
wt switch pr:<number> -x codex
```

After changes:

```bash
git status --short
gh pr checks --watch
```

## Optional Keybinding Targets

TUI keybindings should call a thin helper or `wt` directly:

```bash
dev-handoff wt <owner/repo> pr:<number>
dev-handoff codex <owner/repo> pr:<number> -- "<task prompt>"
dev-handoff review <owner/repo> pr:<number> <number>
```

Keep the helper narrow: resolve the repo, then delegate to `wt`, `gh`, the selected agent, or the selected TUI.
