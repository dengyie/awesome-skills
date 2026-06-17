# Best Project Memory V6 Session Compaction Plan

> Status: In progress.
> Target package: `best-project-memory`
> Phase type: governance helper completion

## Goal

Implement the missing V2 session-compaction helper so long-running repositories can reduce `session-log.md` reading cost without deleting continuity.

This phase should add a deterministic `compact_session.py` workflow that:

1. reads structured `session-log.md` entries
2. compacts older entries into a durable phase-style summary or compacted history block
3. preserves recent entries for active work
4. keeps exact next actions, blockers, and validation-relevant signals easy to recover

## Why This Phase

The V2 governance plan explicitly calls for session compaction, but the package still stops at append-only history plus handoff generation.

Current gap:

- `session-log.md` can grow indefinitely
- `update-triggers.md` already names compaction as a first-class event
- long-running Level 3 integrations will eventually pay a real reading-cost penalty
- there is no deterministic helper yet for reducing that cost while keeping repo-native history trustworthy

This means the shipped V2 package still lacks one of its core governance loops.

## Scope

In scope:

- add `best-project-memory/scripts/compact_session.py`
- define a conservative compaction format for `session-log.md`
- optionally emit a phase summary into `.codex-memory/phases/`
- keep the newest active entries unmodified
- update package docs and tests
- run package validation and production review

Out of scope:

- deleting historical files
- rewriting `project-state.md` or `todo.md` automatically as part of compaction
- natural-language summarization of ambiguous logs without clear structure
- adding a background daemon or CI integration

## Proposed Behavior

### Input assumptions

The helper will assume `session-log.md` mostly follows the documented entry shape:

- `## YYYY-MM-DD HH:mm`
- `- Task:`
- `- Actions:`
- `- Results:`
- `- Next:`
- `- Blockers:`

If malformed entries are encountered, the helper should keep them rather than guessing aggressively.

### Compaction strategy

Default behavior:

- keep the newest `N` entries in `session-log.md`
- compact older well-formed entries into a single summary block
- prepend the compacted block to `session-log.md` so the operator still sees that history existed

Optional behavior:

- when requested, also write a phase summary file under `.codex-memory/phases/`

### Summary content

The compacted block should preserve:

- covered date range
- number of entries compacted
- high-signal task/results bullets
- unresolved blockers if any existed
- next-step themes that still matter historically

The helper should avoid:

- transcript-style output
- duplicating every original line
- pretending to resolve conflicting statements automatically

## CLI Shape

Proposed arguments:

- `--repo`
- `--keep-last <int>`
- `--max-entries <int>` as a threshold gate
- `--phase-slug <slug>` optional phase artifact output
- `--title <text>` optional summary title override
- `--dry-run`

Behavior notes:

- if entry count is below threshold, do nothing and exit cleanly
- `--dry-run` should print what would change without rewriting files
- phase output should be additive, not destructive

## File Changes

### Add

- `best-project-memory/scripts/compact_session.py`
- `docs/dev/2026-06-18-best-project-memory-v6-session-compaction-plan.md`

### Modify

- `best-project-memory/SKILL.md`
- `best-project-memory/tests/test_skill_package.py`
- `docs/usage/best-project-memory.md`
- `CHANGELOG.md`
- `.codex-memory/*` state files for this repository

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- `compact_session.py` exists and behaves deterministically
- compaction preserves recent entries and summarizes older structured history
- optional phase output is generated when requested
- package tests cover the new helper and package surface
- package validation passes
- production review is run and confirmed findings are fixed

## Tasks

- [ ] Implement `compact_session.py`.
- [ ] Add regression coverage for compaction behavior and no-op thresholds.
- [ ] Update package docs and helper inventory.
- [ ] Run tests, validation, and production review.
- [ ] Fix confirmed findings.
- [ ] Update project memory, commit, and push.
