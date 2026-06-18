# Best Project Memory V12 Stale TODO Hardening Plan

> Status: In progress.
> Target package: `best-project-memory`
> Phase type: quality-control hardening

## Goal

Expand `stale_todo_check.py` so it detects not only vague wording, but also obviously stale or dirty active TODO state that no longer matches the surrounding memory evidence.

## Why This Phase

The V2 governance plan describes `stale_todo_check.py` as responsible for:

- detecting long-unmoved TODO items
- surfacing invalid or dirty active task state

Current gap:

- the script only checks for vague wording such as `cleanup` or `keep improving this`
- it does not inspect nearby memory evidence for stale active items
- it does not help catch active TODOs that should likely have moved to `Done`

That means one of the named Phase 4 quality controls is still underpowered relative to the original V2 design.

## Scope

In scope:

- strengthen `best-project-memory/scripts/stale_todo_check.py`
- add deterministic heuristics for stale or dirty active TODO state
- add regression coverage
- update usage docs and project memory
- run tests, validation, and production review

Out of scope:

- semantic AI-style classification of arbitrary task intent
- automatic TODO rewriting or reordering
- changing `memory_lint.py`

## Proposed Behavior

### Existing checks to keep

- fail on vague active items such as one-word placeholders or known weak phrases

### New stale-state checks

Flag active TODO items when repo memory strongly suggests they are stale or dirty, for example:

- an item in `## In Progress` or `## Next` exactly matches an already completed `## Done` item after lightweight normalization
- an active item exactly matches a recent `Next:` line in `session-log.md` while the same normalized item already appears in `## Done`

Normalization should stay conservative:

- lowercase
- trim whitespace
- collapse repeated spaces
- strip checkbox/list prefixes

### Non-goals

Do not:

- infer completion from loose semantic similarity
- rewrite files automatically
- fail merely because there are many active items

## File Changes

Modify:

- `best-project-memory/scripts/stale_todo_check.py`
- `best-project-memory/tests/test_skill_package.py`
- `docs/usage/best-project-memory.md`
- `.codex-memory/project-state.md`
- `.codex-memory/todo.md`
- `.codex-memory/session-log.md`
- `.codex-memory/decisions.md`
- `CHANGELOG.md`

Add:

- `docs/dev/2026-06-18-best-project-memory-v12-stale-todo-hardening-plan.md`

## Acceptance Criteria

- vague active TODO items still fail the check
- an active TODO duplicated in `## Done` fails the check
- regression tests cover at least one stale duplicate scenario
- docs explain the stronger stale-state behavior
- package validation and production review pass

## Validation

- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Tasks

- [ ] Harden `stale_todo_check.py`.
- [ ] Add regression coverage for stale duplicate active items.
- [ ] Update usage docs and project memory.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Commit and push the V12 stale-todo hardening pass.
