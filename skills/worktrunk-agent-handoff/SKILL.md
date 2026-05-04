---
name: worktrunk-agent-handoff
description: Start Codex, Goose, or another coding agent in isolated WorkTrunk worktrees with GitHub PR and checks context.
metadata:
  tags: worktrunk, wt, codex, goose, github, worktree, pr-review
---

# WorkTrunk Agent Handoff

Use this skill when a user wants an AI agent to start work on a PR, branch, issue, fix, or follow-up task using WorkTrunk-managed git worktrees.

The goal is a command-line flow that agents can execute directly:

- `wt` owns worktree creation, switching, merge, and cleanup.
- `gh` owns scriptable GitHub PR, review, checks, and run context.
- `codex`, `goose`, or another agent runs inside the selected worktree.
- `gh-dash`, `gh-enhance`, lazygit, Neovim, Diffview, and Octo are optional human-facing views around the same state.

## Preferred Commands

Start Codex on an existing GitHub PR:

```bash
wt switch pr:<number> -x codex
```

Start Codex on a new independent branch:

```bash
wt switch --create <branch> -x codex -- "<task prompt>"
```

Start Codex on a stacked follow-up branch from the current worktree:

```bash
wt switch --create <branch> --base=@ -x codex -- "<task prompt>"
```

Start Goose or another agent:

```bash
wt switch pr:<number> -x goose
wt switch --create <branch> --base=@ -x '<agent command>' -- "<task prompt>"
```

If the user has a helper such as `dev-handoff`, it should stay thin and delegate to the same primitives:

```bash
dev-handoff codex <owner/repo> pr:<number> -- "<task prompt>"
dev-handoff codex-current <branch> -- "<task prompt>"
dev-handoff review <owner/repo> pr:<number> <number>
```

## Agent PR Workflow

1. Resolve the target.

   ```bash
   gh pr view <number> --json number,title,headRefName,baseRefName,author,url,reviewDecision
   gh pr checks <number>
   ```

2. Enter the isolated worktree.

   ```bash
   wt switch pr:<number>
   ```

3. Inspect current state from inside the worktree.

   ```bash
   git status --short --branch
   gh pr view --json number,title,body,comments,reviews,reviewDecision
   gh pr diff --name-only
   ```

4. Execute the task with the chosen agent.

   ```bash
   wt switch pr:<number> -x codex
   ```

5. Validate with repo-native commands and scriptable GitHub checks.

   ```bash
   git status --short
   gh pr checks
   gh run list --limit 10
   ```

6. Report branch, worktree path, PR number, validation status, and remaining risks.

## TUI Tools

Use terminal UIs for human selection and review, not as required agent dependencies:

- `gh-dash`: PR inbox and triage. A row action can launch `wt switch pr:<number> -x codex`.
- `gh-enhance`: GitHub Actions/checks TUI. Agents should prefer `gh pr checks`, `gh run view`, or `gh run watch`.
- `lazygit`: local git shaping, branch cleanup, stash, rebase, and worktree visibility.
- Neovim Diffview/Octo: code review, line comments, PR metadata, and final human review.

## Codex Linked Worktrees

Codex can hit git write failures in linked worktrees because writes land in the shared common git directory. If that happens, check:

```bash
git rev-parse --path-format=absolute --git-dir --git-common-dir
```

If the git dir and common dir differ, relaunch with a profile that permits shared git metadata writes:

```bash
codex -p worktree-git
```

Or use a shell wrapper that applies that profile only inside linked worktrees.

## Rules

- Use `wt`, not raw `git worktree`, for lifecycle actions.
- Prefer `gh` commands for autonomous PR and checks context.
- Treat `gh-dash`, `gh-enhance`, lazygit, Diffview, and Octo as optional human-facing entrypoints unless the user explicitly asks to open them.
- Do not merge, delete branches, or remove worktrees unless the user asks to finish or clean up.
- Keep execution inside the selected worktree.
- Report exact commands used when starting an agent task.
