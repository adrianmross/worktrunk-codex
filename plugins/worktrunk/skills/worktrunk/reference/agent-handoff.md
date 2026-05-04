# Agent Handoff Pipeline

This guide describes a WorkTrunk-centered flow that both humans and AI agents can execute.

The durable boundary is:

- `wt` owns worktree creation, switching, merge, and cleanup.
- `gh` owns GitHub state that agents need to query or change.
- `codex`, `goose`, or another agent runs inside the selected worktree.
- `gh-dash`, `gh-enhance`, `lazygit`, Neovim, Diffview, and Octo are human-facing TUIs around the same state.

Agents should prefer the non-TUI command path. Humans can use the TUIs to choose context and then launch the same commands.

## Core Patterns

Start Codex on an existing PR branch:

```bash
wt switch pr:<number> -x codex
```

Start Codex on a new branch from the default branch:

```bash
wt switch --create <branch> -x codex -- "<task prompt>"
```

Start Codex on a stacked follow-up branch from the current worktree:

```bash
wt switch --create <branch> --base=@ -x codex -- "<task prompt>"
```

Start another agent instead of Codex:

```bash
wt switch <target> -x '<agent command>'
```

Examples:

```bash
wt switch pr:123 -x goose
wt switch --create fix-login --base=@ -x 'goose session'
```

Use `wt switch --help` to confirm how arguments after `--` are passed to the executed command for the installed WorkTrunk version.

## Agent-Native PR Flow

1. Resolve the work item.

   ```bash
   gh pr view <number> --json number,title,headRefName,baseRefName,author,url
   gh pr checks <number>
   ```

2. Enter the isolated worktree.

   ```bash
   wt switch pr:<number>
   ```

3. Inspect the state from inside the worktree.

   ```bash
   git status --short --branch
   gh pr view --json number,title,body,comments,reviews,reviewDecision
   gh pr diff --name-only
   ```

4. Execute the task with the chosen agent.

   ```bash
   wt switch pr:<number> -x codex
   ```

5. Validate using repo-native commands, then update the PR.

   ```bash
   git status --short
   gh pr checks
   gh pr comment --body "<summary>"
   ```

6. Merge or clean up only when the user explicitly asks.

   ```bash
   wt merge
   wt remove @
   ```

## Human TUI Integration

Use TUIs for selection, review, and local git shaping:

- `gh-dash`: PR inbox and triage. A row action can launch `wt switch pr:<number> -x codex`.
- `gh-enhance`: GitHub Actions/checks TUI. Agents should use `gh pr checks`, `gh run view`, or `gh run watch` for scriptable checks.
- `lazygit`: local branch, commit, stash, rebase, and worktree visibility. A custom command can run `wt switch <branch> -x codex`.
- Neovim Diffview/Octo: code review, line comments, PR metadata, and final human review.

The TUI tools should not be required for an agent to complete the task. They should call into the same shell helpers or `wt` commands that agents can run directly.

## Suggested Shell Helper Surface

A user may expose a thin helper such as `dev-handoff` to normalize repo resolution and TUI keybindings:

```bash
dev-handoff wt <owner/repo> pr:<number>
dev-handoff codex <owner/repo> pr:<number> -- "<task prompt>"
dev-handoff review <owner/repo> pr:<number> <number>
dev-handoff codex-current <branch> -- "<task prompt>"
```

This helper should stay small:

- Resolve a repo slug to a local checkout.
- Delegate worktree lifecycle to `wt`.
- Delegate GitHub state to `gh`.
- Delegate interactive review to Neovim, lazygit, `gh-dash`, or `gh-enhance`.
- Avoid replacing `wt`, `gh`, or the agent CLI with a large wrapper.

## Codex Linked Worktree Sandbox

In linked worktrees, Codex may need a profile that can write the shared git directory. If git writes fail, verify:

```bash
git rev-parse --path-format=absolute --git-dir --git-common-dir
```

If those paths differ, relaunch Codex with a linked-worktree profile:

```bash
codex -p worktree-git
```

Or use a shell wrapper that automatically applies that profile only inside linked worktrees.

## Agent Rules

- Use `wt`, not raw `git worktree`, for lifecycle actions.
- Prefer command-line `gh` queries over opening TUIs when acting autonomously.
- Treat `gh-dash`, `gh-enhance`, `lazygit`, Diffview, and Octo as user-facing views unless the user asks to open them.
- Do not merge, delete branches, or remove worktrees unless the user asked for finish/cleanup behavior.
- Keep task execution inside the selected worktree and report the branch, path, validation, and PR state.
