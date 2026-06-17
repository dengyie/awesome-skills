# Examples

Use these examples as style targets. Adapt them to the actual repository and task.

## Example `project-state.md`

```md
# Project State

## Objective
- Harden the `production-code-quality-review` skill for installed-copy updates.

## Current Phase
- Release hardening

## Current Branch
- codex/review-skill-update-flow

## Last Verified
- `python3 -m unittest discover production-code-quality-review/tests -v`

## Active Risks
- Installed copies can drift from the source checkout if update metadata is missing.

## Active Blockers
- None.

## Current Focus
- Finish regression coverage for update-local-skill installed-copy behavior.

## Next Milestone
- Ship `v0.1.3` with passing tests and release notes.

## Key Artifacts
- `production-code-quality-review/scripts/update-local-skill.sh`
- `production-code-quality-review/tests/test_install_update_flow.py`
```

## Example `session-log.md` entry

```md
## 2026-06-17 14:20
- Task: Harden installed-copy update flow for the review skill.
- Actions: Read install/update helpers, reproduced the failure mode, patched source-path recording, and added regression tests.
- Results: Installed copies now refresh from the recorded source checkout instead of self-deleting.
- Next: Run the release verification bundle and update release notes.
- Blockers: None.
```

## Example `decisions.md` entry

```md
## 2026-06-17 - Record source checkout in installed skill copies
- Decision: Persist the source checkout path in a marker file inside installed copies.
- Rationale: Update tooling must know where to pull a fresh copy from when invoked outside the source repo.
- Alternatives considered: Require users to pass a source path manually on every update.
- Impact: Installed copies become self-describing and updateable with less operator error.
- Rollback trigger: Revisit if the recorded path proves unstable across supported platforms.
- Related files: `production-code-quality-review/scripts/install-local-skill.sh`, `production-code-quality-review/scripts/update-local-skill.sh`
```

## Example `todo.md`

```md
# TODO
## In Progress
- [ ] Finalize release notes for `v0.1.3`
## Next
- [ ] Run `verify-release.sh`
- [ ] Publish the updated install guidance
## Done
- [x] Patch installed-copy update flow
- [x] Add regression coverage
```

## Example handoff skeleton

```md
# Handoff

## Objective
- Finish browser QA for the landing page redesign.

## Current State
- Desktop layout is aligned with the approved mockup.
- Mobile nav still needs overflow checks.

## Read First
- `docs/qa/mobile-nav-report.md`
- `src/components/header.tsx`

## Exact Next Actions
- Run mobile browser QA at 390x844.
- Verify menu open/close state and body scroll lock.
- Update `project-state.md` and `todo.md` with results.

## Blockers
- None.
```
