Finish work on the current WorkTrunk-managed branch.

Workflow:

1. Inspect the worktree state with `wt list` and `git status --short`.
2. If changes are ready, commit or squash using the repo's existing flow.
3. Merge with `wt merge` unless the user asked for a different integration path.
4. If the branch is finished and the user wants cleanup, remove the worktree with `wt remove @`.

Notes:

- Prefer `wt merge` over hand-written git merge commands because it respects WorkTrunk hooks and commit-generation settings.
- If hooks need approval in a non-interactive flow, explain the constraint instead of forcing `--yes` without user intent.
