# Best Project Memory V11 Repair Hardening Plan

> Status: In progress.
> Target package: `best-project-memory`
> Phase type: governance helper hardening

## Goal

Turn `init_memory.py --repair` from a minimal directory backfill into a documented, regression-protected recovery path for incomplete `.codex-memory/` layouts.

## Why This Phase

The V2 governance plan explicitly calls out `init / repair` as part of the tested helper surface.

Current gap:

- `init_memory.py` exposes `--repair`
- but the current behavior is only a thin alias for creating missing core files and optional directories
- there is no explicit regression coverage proving repair on partially broken memory layouts
- release-facing docs do not explain what repair is expected to fix

That leaves one of the named V2 helper promises under-proven compared with the stronger evidence now available for compaction, linting, and multi-skill integration.

## Scope

In scope:

- harden `best-project-memory/scripts/init_memory.py` repair behavior
- make repair deterministic for partial `.codex-memory/` layouts
- add regression coverage for realistic repair scenarios
- update usage docs and project memory
- run package validation and production review

Out of scope:

- semantic repair of corrupted human-authored content
- auto-rewriting non-empty existing files
- new helper scripts
- changes to other skill packages

## Proposed Behavior

### Repair contract

When `--repair` is used:

- ensure `.codex-memory/` exists
- restore any missing core files
- restore governance directories: `phases/`, `handoffs/`, `workstreams/`, `snapshots/`
- optionally create a starter workstream when `--default-workstream` is also provided
- optionally create an initial snapshot when `--default-snapshot` is also provided
- never overwrite existing non-missing files

### Output expectations

The command should stay deterministic and safe:

- return success when repair completes
- print the repaired memory root path
- leave existing content untouched except for newly created missing files or directories

## File Changes

Modify:

- `best-project-memory/scripts/init_memory.py`
- `best-project-memory/tests/test_skill_package.py`
- `docs/usage/best-project-memory.md`
- `.codex-memory/project-state.md`
- `.codex-memory/todo.md`
- `.codex-memory/session-log.md`
- `.codex-memory/decisions.md`
- `CHANGELOG.md`

Add:

- `docs/dev/2026-06-18-best-project-memory-v11-repair-hardening-plan.md`

## Acceptance Criteria

- `--repair` restores missing core files in a partial memory tree
- `--repair` restores governance directories in a partial memory tree
- existing non-missing files are not overwritten during repair
- regression tests cover at least one partial broken-layout repair scenario
- usage docs describe repair expectations clearly
- package tests and production review pass

## Validation

- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Tasks

- [ ] Harden `init_memory.py --repair`.
- [ ] Add regression coverage for partial memory repair.
- [ ] Update usage docs and project memory.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Commit and push the V11 repair-hardening pass.
