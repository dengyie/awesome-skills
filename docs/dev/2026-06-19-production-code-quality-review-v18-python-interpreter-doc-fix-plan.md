# V18 Python Interpreter Documentation Fix Plan

## Milestone

Make `production-code-quality-review` command examples portable across Windows and POSIX Python installations.

## Goal

Remove the production-readiness review gap where the skill tells Windows users to run `python3` even when the active interpreter is available as `python` and the `python3` launcher is broken.

## P0/P1 Scope

- P1: Update the skill's mandatory setup text so users run the active Python interpreter, with `python` on Windows and `python3` on POSIX as examples.
- P1: Update the most visible README and usage examples that users copy during local review setup.
- P1: Add regression coverage so the skill body keeps the portable interpreter guidance.

## Out Of Scope P2/P3

- Do not rewrite all historical docs that mention `python3`.
- Do not change helper script shebangs.
- Do not change generated safe-check command output in this milestone.

## Manual Required

- None.

## Phase Limit

1 phase.

## Acceptance Criteria

- `production-code-quality-review/SKILL.md` no longer presents `python3` as the only mandatory setup command.
- README and review workflow usage docs include active-interpreter guidance.
- Regression tests pass.
- Skill validation passes.

## Stop Conditions

Stop after the doc fix is implemented, verified, committed, and pushed.
