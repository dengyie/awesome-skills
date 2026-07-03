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

## Recommended Reading Order

Use this order to avoid reading the same rule from three places:

1. `design.md`
   - read when you need intent, invariants, rollout strategy, or architecture direction
2. `implementation-plan.md`
   - read when you need the active milestone scope, phase order, acceptance criteria, or stop conditions
3. `split-image-assets/SKILL.md`
   - read when you need the agent-facing runtime workflow entrypoint
4. package references by topic:
   - `references/workflow.md`: state machine and gate runbook
   - `references/asset-package-contract.md`: package contract and validator truth surface
   - `references/pipeline-recipes.md`: route and recipe selection
   - `references/ui-atomic-split.md`: UI-specific planning and routing
   - `references/qa-standards.md`: review and quality criteria
5. `docs/usage/split-image-assets.md`
   - read when you need the user-facing quick operating guide rather than the full contract

## Package Boundary

This directory governs the repo-level design and plan surface.

The package-local runtime surface still lives in:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`

Those files are downstream reflections of this directory, not parallel authorities.
