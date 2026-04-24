Clear a stale WorkTrunk marker for the current branch.

Use this when `wt list` still shows `💬` or `🤖` for a branch after the Codex session is gone.

Run:

```bash
wt config state marker clear
```

If you need to clear a different branch:

```bash
wt config state marker clear --branch <branch>
```
