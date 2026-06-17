# Zero-To-Website Design V22 Memory Shipped State Sync Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: project-memory consistency hardening

## Goal

Synchronize the repository memory artifacts with the already-pushed V21 public workflow alignment commit so the resume surface reflects the shipped state instead of the working-tree state.

## Why This Phase

V21 is already committed and pushed as `4c7f575 docs(阶段30): align public workflow summary`, but the current memory snapshot still says:

- V21 is implemented in the working tree
- the next action is to commit and push V21

That is a small but real consistency bug in the repo-native memory contract.

## Target Outcome

After this phase:

- `project-state.md` says V21 is shipped
- `workstreams/zero-to-website-design-integration.md` says V21 is shipped
- `session-log.md` includes a V21 closeout entry
- `todo.md` no longer lists V21 as pending commit/push

## Scope

In scope:

- update `.codex-memory/project-state.md`
- update `.codex-memory/workstreams/zero-to-website-design-integration.md`
- append `.codex-memory/session-log.md`
- update `.codex-memory/todo.md`
- optionally add a short decision entry if the state transition needs durable capture

Out of scope:

- changes to `README.md`
- changes to `docs/usage/zero-to-website-design.md`
- changes to the skill package code or tests

## Concrete Gaps To Close

### 1. Project state still lags behind Git

The latest stage should be recorded as shipped, not merely implemented.

### 2. Workstream still carries pre-closeout wording

The workstream needs to stop pointing at a commit/push task that already happened.

### 3. TODO still implies V21 is open

The next actionable item should be the next bounded target selection, not V21 closeout.

## Proposed Changes

### `project-state.md`

- change the current phase to shipped for V21
- move current focus back to next-target selection

### `workstreams/zero-to-website-design-integration.md`

- mark V21 as shipped with commit `4c7f575`
- remove the pending commit/push action

### `session-log.md`

- append a brief closeout entry for the V21 shipped-state sync

### `todo.md`

- remove the pending V21 commit/push action
- keep next-target selection as the active next step

## Test Plan

- inspect the updated `.codex-memory` files for consistency
- run `production-code-quality-review` against the working tree

## Acceptance Criteria

- no memory file says V21 is only implemented in the working tree
- the next action is the next target selection, not V21 closeout
- production review passes with no blocking finding

## Decision Record

- Decision: Use a dedicated V22 memory-state sync pass to reconcile `.codex-memory` with the already-shipped V21 Git state.
- Rationale: The repository explicitly treats filesystem memory as the authoritative resume surface, so state drift should be corrected immediately after a push.
- Risk: This can look like housekeeping.
- Mitigation: Keep the scope narrow, deterministic, and tied to authoritative state reconciliation.

## Suggested Commit Shape

- `chore(阶段31): sync memory shipped state`
