# Split Image Assets Docs

This directory is the single documentation entrypoint for `split-image-assets`.

## Authority

Future `split-image-assets` work must converge here first.

When behavior, contract, workflow, or architecture changes:

1. update `design.md` if intent or invariants change
2. update `implementation-plan.md` if execution scope or phase ordering changes
3. update package-facing docs:
   - `split-image-assets/SKILL.md`
   - `split-image-assets/references/*.md`
   - `docs/usage/split-image-assets.md`
4. update code and tests

Do not create new dated `split-image-assets` specs or plans under `docs/superpowers/specs/` or `docs/superpowers/plans/`.

## Files

- `design.md`
  - canonical design authority
  - defines execution contract, asset routing contract, formal-state rules, and architecture direction
- `implementation-plan.md`
  - canonical implementation plan
  - defines the active milestone, phase boundaries, acceptance criteria, and stop conditions
- `migration.md`
  - minimal historical migration note
  - records which older docs were retired and why this directory exists

## Package Boundary

This directory governs the repo-level design and plan surface.

The package-local runtime surface still lives in:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`

Those files are downstream reflections of this directory, not parallel authorities.
