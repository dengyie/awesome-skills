# Best Project Memory V7 Quality Drift Hardening Plan

> Status: In progress.
> Target package: `best-project-memory`
> Phase type: Phase 4 quality-control hardening

## Goal

Strengthen the shipped quality-control layer so `best-project-memory` can detect more real drift, not just missing sections.

This phase should harden `memory_lint.py` around the two biggest remaining blind spots:

1. long-running `session-log.md` history that is clearly ready for compaction but never flagged
2. obvious disagreement between `project-state.md` verification claims and the latest generated snapshot evidence

## Why This Phase

The V2 plan already defines Phase 4 as a quality-control phase focused on preventing memory drift.

Current gap:

- `memory_lint.py` mainly checks structural presence and a few lightweight consistency rules
- `compact_session.py` now exists, but there is no lint reminder when `session-log.md` keeps growing without compaction
- `snapshot_state.py` can write evidence, but there is no lint check that compares the current snapshot panel against the latest snapshot artifact

That means the package now has more governance helpers than enforcement around them.

## Scope

In scope:

- harden `best-project-memory/scripts/memory_lint.py`
- detect when `session-log.md` has too many structured entries without any compacted-history marker
- detect when `project-state.md` says a snapshot was recorded but the referenced snapshot file is missing
- detect when the latest snapshot says changed files exist but `project-state.md` still presents a stale verification panel that hides that evidence
- add regression coverage
- update docs if lint expectations change
- run validation and production review

Out of scope:

- auto-repairing project memory from lint
- changing the snapshot schema itself
- adding full semantic diffing between every memory object

## Proposed Checks

### Session compaction reminder

`memory_lint.py` should warn when:

- `session-log.md` contains more than a configurable number of structured entries
- and no `## Compacted History` block is present

This should stay a warning, not a hard error, because some repos may intentionally keep short-lived raw history.

### Snapshot reference integrity

`memory_lint.py` should error when:

- `project-state.md` contains a `Snapshot:` reference
- but the referenced file under `.codex-memory/snapshots/` does not exist

This is hard evidence drift and should be treated as a real failure.

### Snapshot-vs-state visibility drift

`memory_lint.py` should warn when:

- the latest referenced snapshot reports changed files
- and `project-state.md` still presents only old verification bullets without a current snapshot reference or current evidence hook

The aim is not perfect semantic equivalence, only detection of obvious “filesystem truth exists but the state panel is pretending everything is settled” cases.

## File Changes

### Add

- `docs/dev/2026-06-18-best-project-memory-v7-quality-drift-hardening-plan.md`

### Modify

- `best-project-memory/scripts/memory_lint.py`
- `best-project-memory/tests/test_skill_package.py`
- `docs/usage/best-project-memory.md` if lint guidance changes
- `CHANGELOG.md`
- `.codex-memory/*` state files for this repository

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- `memory_lint.py` detects missing referenced snapshots as errors
- `memory_lint.py` warns when long session history has not been compacted
- regression tests cover the new drift checks
- package tests and validation pass
- production review is run and confirmed findings are fixed

## Tasks

- [ ] Harden `memory_lint.py` for session-compaction and snapshot-drift checks.
- [ ] Add regression coverage.
- [ ] Update docs if the lint expectations change.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Update project memory, commit, and push.
