# Production Code Quality Review V9 Follow-Up Routing Plan

> Status: In progress.
> Target package: `production-code-quality-review`
> Phase type: Level 2 integration hardening

## Goal

Harden the V8 Level 2 review-write path so review follow-up TODO items are routed more predictably and do not accumulate noisy duplicates.

This phase should keep the current opt-in model while improving how follow-up items are merged into `.codex-memory/todo.md`.

## Why This Phase

V8 proved that the review package can append continuity to project memory, but the TODO merge behavior is still intentionally simple.

Current gap:

- every follow-up currently lands in `## Next`
- there is no distinction between urgent review actions and lower-priority follow-ups
- duplicate or near-duplicate review actions can pile up over repeated review cycles

The next step should improve that routing without turning the review skill into a full project manager.

## Scope

In scope:

- improve follow-up routing inside `production-code-quality-review/scripts/review_skill_lib.py`
- support opt-in routing of urgent items into `## In Progress`
- dedupe repeated follow-up items more carefully
- keep the behavior deterministic and conservative
- add regression coverage
- run tests, validation, and production review

Out of scope:

- automatic workstream mutation
- decision promotion
- handoff generation
- fuzzy semantic clustering of arbitrary English TODO items

## Proposed Behavior

### Routing rule

Follow-up items should route to:

- `## In Progress` when they are explicitly marked urgent or blocking
- `## Next` otherwise

Suggested explicit markers:

- prefix `P1:`
- prefix `Blocker:`
- prefix `Urgent:`

The stored TODO text should strip the marker while preserving the actionable wording.

### Dedupe rule

The merge logic should avoid re-adding an item when:

- the exact normalized text already exists in `In Progress`
- or the exact normalized text already exists in `Next`

Normalization should be lightweight:

- trim whitespace
- lowercase
- strip the urgency marker prefix

## File Changes

### Add

- `docs/dev/2026-06-18-production-code-quality-review-v9-followup-routing-plan.md`

### Modify

- `production-code-quality-review/scripts/review_skill_lib.py`
- `production-code-quality-review/tests/test_review_skill_lib.py`
- `production-code-quality-review/tests/test_collect_review_context_cli.py`
- `production-code-quality-review/README.md` if examples change
- `CHANGELOG.md`
- `.codex-memory/*` state files for this repository

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- urgent follow-up items route into `## In Progress`
- non-urgent follow-up items route into `## Next`
- repeated follow-up items do not duplicate across active TODO sections
- regression tests cover the routing and dedupe rules
- validation passes
- production review is run and confirmed findings are fixed

## Tasks

- [ ] Implement follow-up routing and dedupe hardening.
- [ ] Add regression coverage.
- [ ] Update docs if the examples change.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Update project memory, commit, and push.
