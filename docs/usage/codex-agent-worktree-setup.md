# Codex Agent Worktree Setup

Use `codex-agent-worktree-setup` when a Codex thread or development process needs its own branch-bound worktree, or when an existing Codex worktree is detached or incorrectly bound to the primary checkout.

A Git branch or worktree and a Codex-visible thread are separate objects. The skill aligns both: Git provides branch isolation, while Codex thread tools provide the process that appears in the app.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- create a Codex-visible development thread with an isolated worktree
- bind a new Codex worktree to a requested branch
- repair a Codex worktree that is on detached HEAD
- explain why a manually created Git worktree is not visible as a Codex thread
- protect a primary `main` or `master` checkout while parallel development proceeds elsewhere

Do not use it when you only need a temporary branch in the current checkout, or when the user has not asked for a new Codex thread or isolated development process.

## Safety Boundaries

- Never develop directly in the primary `main` or `master` worktree.
- Stop if the primary worktree has uncommitted changes and clarify who owns them.
- Stop if the target branch is already checked out in another worktree; report the occupying path instead of stealing or deleting it.
- Repair detached HEAD only after confirming that the Codex worktree is clean and the target branch is unoccupied.
- Never remove a manual worktree or protected agent branch without explicit approval.

## Workflow

1. Inspect the repository root, current branch, status, worktree list, and local/remote target branch refs.
2. Determine whether the user needs Git isolation only or a Codex-visible thread.
3. For a Codex-visible thread, locate the Codex project and ensure the target branch ref exists.
4. Create the thread with an isolated worktree and the requested branch starting state.
5. Confirm that the thread exists and give it a descriptive title.
6. Verify both the primary checkout and the new worktree before development begins.

## Verification

In the primary worktree, confirm its branch and status are unchanged:

```bash
git branch --show-current
git status --short --branch
```

In the Codex-managed worktree, confirm the requested branch is checked out and the worktree is clean:

```bash
git branch --show-current
git status --short --branch
```

Finally inspect the global mapping:

```bash
git worktree list --porcelain
```

Acceptance requires a Codex-visible thread, an independent worktree path, and the exact requested branch rather than detached HEAD.

## Prompt

```text
Use $codex-agent-worktree-setup to create an isolated Codex worktree on the requested branch while keeping the primary main worktree unchanged.
```

## Related Docs

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [Troubleshooting](troubleshooting.md)
- [Golden Path](golden-path.md)
