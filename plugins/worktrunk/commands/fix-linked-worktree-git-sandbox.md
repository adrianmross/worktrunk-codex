Fix Codex git permission failures inside a linked git worktree.

Rules:

- If git writes fail in a `wt`-managed or `git worktree`-managed linked worktree, check whether `git rev-parse --path-format=absolute --git-dir --git-common-dir` returns different paths.
- When `--git-dir` and `--git-common-dir` differ, explain that Codex `workspace-write` keeps the shared git dir read-only.
- Prefer relaunching Codex with `codex -p worktree-git` or a shell wrapper that selects that profile automatically.
- Do not claim that adding the worktree path to writable roots is sufficient for linked-worktree git writes.
- Keep using `wt` for worktree lifecycle actions; this command is only about Codex sandbox limitations around git metadata writes.
