# Production Code Quality Review V8 Level 2 Memory Integration Plan

> Status: In progress.
> Target package: `production-code-quality-review`
> Phase type: `best-project-memory` V2 multi-skill integration
> Integration level: Level 2 read + append

## Goal

Upgrade `production-code-quality-review` from a Level 1 read-only memory consumer into a Level 2 integration that can append lightweight review continuity back into repo memory after meaningful review work.

This phase should let the review package:

1. keep the existing read-only context loading behavior
2. optionally emit a review session record into `.codex-memory/session-log.md`
3. optionally surface concrete follow-up items that can refresh `todo.md`
4. stop short of governance-heavy actions such as decision promotion, handoff generation, or compaction

## Why This Phase

The V2 plan explicitly recommends choosing a Level 2 append/update integration after the Phase 5 Level 1 pilot.

Current gap:

- `production-code-quality-review` can read project memory and use it to improve review context
- but the review pass itself leaves no repo-native continuity artifact unless another skill or manual step records it
- this means meaningful review findings and review completion state can still get lost between sessions

This phase closes that gap while keeping the integration lightweight.

## Scope

In scope:

- extend `production-code-quality-review` docs and helper behavior for optional Level 2 memory writes
- append a structured review session entry after review when requested
- optionally refresh `todo.md` with review follow-up items when explicitly provided
- add regression coverage
- run tests, validation, and production review

Out of scope:

- automatic writes on every review without opt-in
- writing to `decisions.md`
- generating handoffs
- changing the review-finding schema to become a full project-management format

## Proposed Behavior

### Review session append

When the repo contains `.codex-memory/` and the caller opts in, the review workflow should be able to append a structured session entry summarizing:

- review scope
- findings status
- major actions taken
- next follow-up

### TODO refresh

When explicit follow-up items are supplied, the review helper may update `todo.md` by inserting or refreshing review-specific next actions.

Guardrails:

- writes should stay opt-in
- existing TODO content should be preserved
- helper behavior should remain deterministic and conservative

### Boundaries

This phase remains Level 2 only:

- read current state
- append session history
- refresh todo state

It should not:

- promote decisions
- mutate workstreams aggressively
- generate handoffs automatically

## Candidate Implementation Shape

Possible delivery paths:

1. extend the review entrypoint with explicit memory-write flags
2. add a small helper in `production-code-quality-review/scripts/` that wraps review output plus memory append behavior
3. keep the current review context collector unchanged except for any metadata needed by tests

Preferred direction:

- keep `collect-review-context.py` read-only
- add opt-in continuity writes close to `review-entrypoint.py` or `review_skill_lib.py`
- reuse `best-project-memory/scripts/append_session.py` semantics rather than inventing a new session format

## File Changes

### Add

- `docs/dev/2026-06-18-production-code-quality-review-v8-level2-memory-integration-plan.md`

### Modify

- `production-code-quality-review/SKILL.md`
- `production-code-quality-review/scripts/review-entrypoint.py`
- `production-code-quality-review/scripts/review_skill_lib.py`
- `production-code-quality-review/tests/test_collect_review_context_cli.py` if needed
- `production-code-quality-review/tests/test_review_skill_lib.py`
- `docs/usage/best-project-memory.md` and/or package docs if integration guidance changes
- `CHANGELOG.md`
- `.codex-memory/*` state files for this repository

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- the review package still supports Level 1 read-only setup behavior
- an opt-in Level 2 path can append a structured review session entry
- an opt-in Level 2 path can refresh review follow-up TODO items conservatively
- regression tests cover the memory-write behavior
- package validation passes
- production review is run and confirmed findings are fixed

## Tasks

- [ ] Implement opt-in Level 2 memory writes for review continuity.
- [ ] Add regression coverage.
- [ ] Update package docs and integration guidance.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Update project memory, commit, and push.
