# Production Code Quality Review V13 Mainline Sync Plan

> Status: Implemented in working tree
> Target surface: `production-code-quality-review`
> Phase type: upstream/mainline synchronization

## Goal

Commit the pending `production-code-quality-review/` working-tree changes only if they are proven to match the current GitHub `origin/main` package state and pass package validation.

## Why This Phase

After the `zero-to-website-design` and repository skill-matrix work landed, the only remaining active TODO was to decide whether to commit the `production-code-quality-review` GitHub sync. The diff is large because it removes the branch-local project-memory review integration and aligns the package with the newer mainline staged-review-mode version.

## Evidence

- `origin/main` is `f1eac464bc5962932df9e8c1b59c9bd59bea37db` (`Refine staged review modes`).
- `git diff --stat origin/main -- production-code-quality-review` reports no package differences.
- `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v` passes.
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review` passes.

## Decision

Commit the sync as a standalone phase.

## Rationale

The repository should not keep a dirty local package state when that state is an exact match for GitHub mainline. Keeping it uncommitted would make later website-generation skill work harder to review and would continue to surface unrelated diffs in production review context.

## Risk

This sync removes the branch-local Level 2 review-memory write path from `production-code-quality-review`. That is acceptable for this phase because `origin/main` is treated as the package source of truth and the repository still retains historical documentation for the earlier memory-integration experiments.

## Acceptance Criteria

- the package matches `origin/main`
- package tests pass
- skill validation passes
- the sync is committed separately from website-generation skill changes
- project memory records that the dirty review package diff has been resolved

## Suggested Commit Shape

- `chore(阶段23): sync production review skill`
