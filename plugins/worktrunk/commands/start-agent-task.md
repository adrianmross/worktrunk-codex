Start an isolated agent task through WorkTrunk.

Use this when the user wants Codex, Goose, or another agent to begin work on a PR, branch, issue, or follow-up task.

Workflow:

1. Resolve the target:
   - Existing PR: `pr:<number>`
   - Existing branch: `<branch>`
   - New independent task: `--create <branch>`
   - New stacked follow-up: `--create <branch> --base=@`

2. Inspect current repo context:

   ```bash
   git status --short --branch
   wt list
   ```

3. For an existing PR, gather GitHub context:

   ```bash
   gh pr view <number> --json number,title,headRefName,baseRefName,author,url,reviewDecision
   gh pr checks <number>
   ```

4. Start the agent through `wt switch -x`.

   Codex:

   ```bash
   wt switch pr:<number> -x codex
   wt switch --create <branch> --base=@ -x codex -- "<task prompt>"
   ```

   Goose or another agent:

   ```bash
   wt switch pr:<number> -x goose
   wt switch --create <branch> --base=@ -x '<agent command>' -- "<task prompt>"
   ```

5. If the agent is Codex and git writes fail in a linked worktree, check:

   ```bash
   git rev-parse --path-format=absolute --git-dir --git-common-dir
   ```

   When the git dir and common dir differ, relaunch with the linked-worktree profile:

   ```bash
   codex -p worktree-git
   ```

6. Report the branch, worktree path, PR number if any, and the exact command used.

Rules:

- Use `wt`, not raw `git worktree`.
- Use `gh` for scriptable PR/check context; do not require `gh-dash`, `gh-enhance`, lazygit, or Neovim for autonomous agent work.
- Treat TUI tools as optional human entrypoints that can call the same `wt` commands.
- Do not merge or remove worktrees unless the user asked to finish or clean up.
