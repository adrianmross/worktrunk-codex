# Command Reference

These are the canonical command-line flows for the WorkTrunk agent handoff skill and Codex plugin.

## Start Agent Work

Start Codex on an existing GitHub PR:

```bash
wt switch pr:123 -x codex
```

Start Codex on a new branch from the default branch:

```bash
wt switch --create fix-login -x codex -- "Fix the login regression"
```

Start Codex on a stacked branch from the current worktree:

```bash
wt switch --create fix-login-followup --base=@ -x codex -- "Address review feedback"
```

Start Goose on a PR branch:

```bash
wt switch pr:123 -x goose
```

Use a custom agent command:

```bash
wt switch --create fix-cli --base=@ -x 'goose session' -- "Fix the CLI regression"
```

## Gather GitHub Context

Inspect a PR before launching an agent:

```bash
gh pr view 123 --json number,title,headRefName,baseRefName,author,url,reviewDecision
gh pr checks 123
gh pr diff 123 --name-only
```

Inspect from inside the PR worktree:

```bash
gh pr view --json number,title,body,comments,reviews,reviewDecision
gh pr checks
git status --short --branch
```

Watch checks after pushing:

```bash
gh pr checks --watch
```

## Install the Standalone Skill

Install from GitHub:

```bash
npx skills add https://github.com/adrianmross/worktrunk-codex --skill worktrunk-agent-handoff
```

Install globally for Codex:

```bash
npx skills add https://github.com/adrianmross/worktrunk-codex --skill worktrunk-agent-handoff -g -a codex
```

Install globally for Goose:

```bash
npx skills add https://github.com/adrianmross/worktrunk-codex --skill worktrunk-agent-handoff -g -a goose
```

List available skills without installing:

```bash
npx skills add https://github.com/adrianmross/worktrunk-codex --list
```

## Linked Worktree Codex Profile

When Codex cannot write git metadata inside a linked worktree, verify the git dir layout:

```bash
git rev-parse --path-format=absolute --git-dir --git-common-dir
```

If the paths differ, relaunch with a linked-worktree profile:

```bash
codex -p worktree-git
```
