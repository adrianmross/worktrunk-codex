Create or switch to a WorkTrunk-managed worktree for the current task.

Rules:

- Use `wt switch --create <branch>` for a new branch from the repo default branch.
- Use `wt switch --create <branch> --base=@` only when the user explicitly wants a stacked follow-up branch on the current worktree.
- Never use raw `git worktree add`.
- Prefer short, kebab-case branch names derived from the task.
- Report the resulting branch name and worktree path.

If the repo has `.config/wt.toml`, let its hooks run instead of reimplementing repo bootstrapping manually.
