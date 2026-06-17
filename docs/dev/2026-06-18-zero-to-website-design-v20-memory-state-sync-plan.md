# Zero-To-Website Design V20 Memory State Sync Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: project-memory consistency hardening

## Goal

Sync the repository memory artifacts so they reflect the actual shipped V19 state instead of leaving resume-critical notes in a partially pre-push posture.

## Why This Phase

V19 is already committed and pushed as `123bfd5 feat(阶段28): harden entrypoint and usage visibility`, but some `.codex-memory` artifacts still say:

- V19 is only implemented in the working tree
- the next action is to commit and push V19
- the latest session block ends before the actual commit and push happened

That drift is small, but it weakens the stated goal of using filesystem memory as the authoritative resume surface.

## Target Outcome

After this phase:

- the workstream records V19 as shipped, not merely implemented
- the workstream next actions move on to choosing V20's successor
- the session log includes the V19 closeout state instead of stopping mid-closeout
- TODO no longer uses a fake `None.` placeholder in `## In Progress`

## Scope

In scope:

- update `.codex-memory/workstreams/zero-to-website-design-integration.md`
- update `.codex-memory/session-log.md`
- update `.codex-memory/todo.md`
- update `.codex-memory/project-state.md` only if needed for consistency

Out of scope:

- new helper scripts
- changes to shipped skill package behavior
- changes to `zero-to-website-design` references or templates

## Concrete Gaps To Close

### 1. Workstream still carries pre-push V19 language

The workstream says V19 is implemented in the working tree and still needs commit/push, which is no longer true.

### 2. Latest session block stops before the actual closeout

The top session entry records implementation and verification, but not the final memory sync, commit, and push.

### 3. TODO active section is structurally awkward

`## In Progress` currently contains `- [ ] None.`. That is not wrong structurally, but it is noisier than simply moving the active work into `## Next` when nothing is running.

## Proposed Changes

### `workstreams/zero-to-website-design-integration.md`

- mark V19 as shipped with commit `123bfd5`
- replace the stale push task with the next target-selection task

### `session-log.md`

- append a small closeout entry for V19 memory sync, commit, and push

### `todo.md`

- remove the placeholder active item
- keep the next hardening-target decision as the next actionable item

## Test Plan

- inspect `git status --short --branch`
- re-read the updated `.codex-memory` files for consistency
- run `production-code-quality-review` against the working tree

## Acceptance Criteria

- no `.codex-memory` artifact still says V19 needs commit/push
- the latest session history names the actual closeout result
- TODO active state is clean and actionable
- production review reports no blocking issue

## Decision Record

- Decision: Use a dedicated V20 memory-state sync pass instead of folding the fixes invisibly into the next feature stage.
- Rationale: The repository explicitly treats filesystem memory as the authoritative resume surface, so state drift in memory artifacts deserves its own bounded correction.
- Risk: This phase could look like housekeeping rather than forward movement.
- Mitigation: Keep the scope narrow, evidence-based, and tied directly to resumability and traceability.

## Suggested Commit Shape

- `chore(阶段29): sync memory shipped state`
