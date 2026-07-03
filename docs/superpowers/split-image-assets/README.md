# Split Image Assets Docs

This directory is the single documentation entrypoint for `split-image-assets`.

## Authority

Future `split-image-assets` work must converge here first.

This directory is the canonical authority for:

- design intent
- current implementation baseline
- documentation ownership boundaries

The package-local docs are runtime reflections of this directory. They should not invent a competing design line.

When behavior, contract, workflow, or architecture changes:

1. update `design.md` if intent, invariants, or truth rules change
2. update `implementation-plan.md` if the current baseline or next bounded milestone changes
3. update package-facing docs:
   - `split-image-assets/SKILL.md`
   - `split-image-assets/references/*.md`
   - `docs/usage/split-image-assets.md`
4. update code and tests

Do not create new dated `split-image-assets` specs or plans under `docs/superpowers/specs/` or `docs/superpowers/plans/`.

## Authority Matrix

Use this table when deciding where a change belongs:

| Surface | Owns | Does not own |
| --- | --- | --- |
| `design.md` | invariants, architecture direction, route truth model, rollout policy | command walkthroughs, script flags, operator shortcuts |
| `implementation-plan.md` | current shipped baseline, latest closed milestone, next bounded milestone candidates | historical execution checklist for already completed work |
| `split-image-assets/SKILL.md` | agent runtime entrypoint, workflow steps, output expectations | canonical architecture decisions when they conflict with `design.md` |
| `references/quick-contract.md` | short truth summary | full field-by-field contract detail |
| `references/asset-package-contract.md` | validator-facing contract and formal state surface | milestone planning |
| `docs/usage/split-image-assets.md` | human/operator guide | canonical truth source |

## Files

- `design.md`
  - canonical design authority
  - defines execution contract, asset routing contract, formal-state rules, and architecture direction
- `implementation-plan.md`
  - canonical current implementation baseline
  - defines the latest closed milestone, the current shipped state, and next bounded milestone candidates
- `migration.md`
  - minimal historical migration note
  - records which older docs were retired and why this directory exists

## Recommended Reading Order

Use this order to avoid reading the same rule from three places:

1. `design.md`
   - read when you need intent, invariants, rollout strategy, or architecture direction
2. `implementation-plan.md`
   - read when you need the current shipped baseline, the latest closed milestone, or the next bounded milestone candidates
3. `split-image-assets/SKILL.md`
   - read when you need the agent-facing runtime workflow entrypoint
4. package references by topic:
   - `references/workflow.md`: state machine and gate runbook
   - `references/asset-package-contract.md`: package contract and validator truth surface
   - `references/provider-contract.md`: upstream provider bridge request/result contract
   - `references/default-route-chains.md`: default provider chains for each planned route
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
- `split-image-assets/references/provider-contract.md`
- `split-image-assets/references/default-route-chains.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`

Those files are downstream reflections of this directory, not parallel authorities.

When in doubt:

- `design.md` wins over package-facing wording
- `asset-package-contract.md` wins over shortcuts in `quick-contract.md`
- `implementation-plan.md` wins over stale TODO-style milestone text elsewhere
