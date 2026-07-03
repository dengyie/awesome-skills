# Split Image Assets Unified Implementation Plan

Date: 2026-07-03
Status: Canonical implementation plan for the current `split-image-assets` planning-first route-control line
Design source: `docs/superpowers/split-image-assets/design.md`

## Authority

This is the single implementation plan for the current `split-image-assets` milestone.

It replaces the prior installer-UX-first implementation plan as the active execution plan for this package line.

All future development on this line should execute from this plan unless a newer canonical plan explicitly replaces it.

## Prior Milestone Disposition

The prior contract-hardening line remains preserved baseline behavior.

The prior installer UX line is no longer the active execution target for this plan. Treat it as backlog unless a concrete blocker requires reopening part of it.

This avoids running multiple canonical milestones in parallel.

## Execution Contract

```text
Milestone: split-image-assets planning-first generation-routing V1
Goal: add whole-image planning, object-route control, and generated-reconstruction truth surfaces so the package can divert bad extraction candidates early without weakening delivery honesty
P0/P1 scope:
- P0: canonical planning-first docs and workflow language
- P0: plan-manifest contract and route taxonomy
- P0: generation-routing gate and route-signal rules
- P0: generated-reconstruction delivery/evidence contract
- P0: validator enforcement for generated-reconstruction truth claims
- P1: generation capability reporting integrated into preflight
- P1: object-level budget and retry boundary rules
- P1: final reporting split for extraction / approximate reconstruction / generated reconstruction
Out-of-scope P2/P3:
- building a built-in segmentation runtime
- building a built-in general image-generation runtime
- whole-image redraw workflows
- automatic multi-round generation optimization
- GUI review or planning tools
- broad installer UX expansion unless directly required for generation capability truthfulness
Manual-required:
- real external segmentation runtimes
- real external generation runtimes
- user approvals for protected objects and generated-object promotions
Phase limit: 4
Phase split:
- Phase 0: canonical alignment and migration tables
- Phase 1: non-breaking planning and capability scaffolding
- Phase 2: generated-reconstruction state and review wiring
- Phase 3: staged validator tightening, reporting, and regression closure
Acceptance criteria:
- the package documents whole-image planning as a hard precondition
- object routes are explicit and auditable
- generated-reconstruction has its own delivery and evidence contract
- preflight reports generation capability using the same readiness vocabulary
- validator rejects generated-delivery drift and silent route dishonesty
- final reporting separates extraction, approximate reconstruction, generated reconstruction, draft candidates, support-only layers, and blocked objects
Stop conditions:
- current P0/P1 scope is complete and verified
- a concrete blocker requires a new canonical milestone
- the phase budget is exhausted without a truthful path to finish the same milestone
```

## Current Diagnosis

This milestone is driven by six concrete issues:

1. there is no hard whole-image planning surface before expensive object work begins
2. route choice between extraction, reconstruction, generation, rebuild, and support is still under-specified
3. generation is not yet represented as a formal delivery route with its own truth contract
4. missing segmentation capability could still tempt an agent into an untruthful generation fallback
5. object-level attempt budgets and route-switch confirmations are not yet first-class
6. final reporting still lacks a route-separated delivery summary

## Phase Strategy

This milestone should land in four bounded phases. The goal is not to rewrite the package in one step, but to establish route-planning truth surfaces first and then wire enforcement behind them.

### Phase 0: Canonical Alignment And Migration Tables

**Phase goal:** remove migration ambiguity before code changes begin.

**Corresponding P0/P1:**

- P0 canonical docs
- P0 route taxonomy
- P0 generated-reconstruction semantics

**Expected deliverables:**

- updated canonical `design.md`
- updated canonical `implementation-plan.md`
- explicit route-mapping tables between `planned_route` and current `decision_routing`
- explicit compatibility matrix for `delivery_class`, `reuse_status`, and pass semantics
- explicit generation provider-class contract
- explicit staged rollout policy for `plan_manifest`

**Required behavior:**

- canonical docs no longer leave route mapping to implementation-time inference
- canonical docs no longer leave status migration to implementation-time inference
- rollout-sensitive rules are marked as staged instead of implied to be immediate

**Verification:**

- docs review for migration completeness

### Phase 1: Non-Breaking Planning And Capability Scaffolding

**Phase goal:** add planning and generation-capability surfaces without breaking the current metadata-first baseline.

**Corresponding P0/P1:**

- P0 plan-manifest contract
- P0 generation-routing gate rules
- P1 generation capability reporting

**Expected deliverables:**

- package-local planning helpers or manifest schema support
- initializer support for planning-state placeholders where needed
- preflight updates in `check_extraction_environment.py`
- route-signal vocabulary for:
  - `recoverability_low`
  - `object_is_reconstruction_like`
  - `quality_target_high`
  - `segmentation_cost_unfavorable`
- generation capability output using:
  - `installed`
  - `runtime_ready`
  - `production_ready`
- provider-class reporting for:
  - `codex-controlled-generation`
  - `external-generated-outputs`
  - `local-model-runtime`
- shared contract additions for planning and generation enums

**Required behavior:**

- this phase remains non-breaking for existing non-generated packages
- no route may silently claim generation-readiness from raw imagegen availability alone
- generation `production_ready` requires transparent object-asset support
- route-to-generate cannot be justified only by missing segmentation tools
- `plan_manifest` support exists before validator hard enforcement widens

**Verification:**

- targeted tests for capability output
- targeted tests for route-signal mappings
- targeted tests proving non-generated legacy-compatible packages do not regress only because planning scaffolding exists

### Phase 2: Generated-Reconstruction State And Review Wiring

**Phase goal:** wire generated-delivery semantics through mutable package state before broad validator tightening.

**Corresponding P0/P1:**

- P0 generated-reconstruction evidence contract
- P0 generated delivery semantics
- P1 budget and retry boundaries

**Expected deliverables:**

- review/update support for generated-object confirmation and promotion
- compare/promotion alignment for generated candidates where needed
- coordinated contract updates for:
  - `delivery_class=generated-reconstruction`
  - generated-specific reuse status
  - budget-related attempt tracking
- metadata/reporting alignment for object-level generated approvals

**Required behavior:**

- new generated statuses must not land in only one layer
- contract constants, review-writer pass gates, validator pass gates, and summary logic must be migrated together
- generated objects cannot pass through package-level final acceptance alone
- generated objects require compare evidence and object-level promotion approval
- missing generation evidence blocks generated delivery claims
- generated assets cannot collapse into plain `production-ready` extraction semantics

**Verification:**

- targeted review-writer tests
- targeted compare/promotion tests where generated flows touch them
- targeted contract-surface tests for synchronized new statuses

### Phase 3: Staged Validator Tightening, Reporting, And Regression Closure

**Phase goal:** tighten validator behavior in a staged way and close reporting/tests/docs around the new route model.

**Corresponding P0/P1:**

- P1 final reporting split
- P1 package-facing closure
- P1 regression depth

**Expected deliverables:**

- staged validator tightening:
  - generated-route `plan_manifest` requirement
  - generated evidence completeness requirement
  - protected-object approval requirement
  - budget-overrun honesty requirement
  - later broader `plan_manifest` rollout only if migration coverage is ready
- final reporting split in package outputs and docs
- regression coverage for:
  - plan-manifest requirement
  - generation capability truthfulness
  - protected-object routing
  - generated evidence completeness
  - budget overrun behavior
  - route-separated final reporting
- final quick validation and package test pass

**Required behavior:**

- package-facing docs must not describe generation as an informal fallback
- final reporting must separate route classes clearly
- tests must fail on missing route or generated-delivery evidence
- validator widening beyond generated-route objects must only happen if fixtures and helpers already cover the migration path

**Verification:**

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

## Detailed Task List

## Phase 0 Tasks

- [ ] Add route-mapping tables to the canonical docs.
- [ ] Add a delivery-state compatibility matrix to the canonical docs.
- [ ] Add generation provider-class definitions to the canonical docs.
- [ ] Add staged `plan_manifest` rollout rules to the canonical docs.

## Phase 1 Tasks

- [ ] Introduce or formalize a `plan_manifest` surface.
- [ ] Add generation capability reporting to `check_extraction_environment.py`.
- [ ] Add route-signal and route-threshold definitions to the shared contract layer.
- [ ] Add budget-related planning fields, attempt tracking, and route-reason requirements.
- [ ] Keep this phase non-breaking for existing non-generated fixtures.

## Phase 2 Tasks

- [ ] Extend review/update flows to record generated-object acceptance and promotion.
- [ ] Coordinate generated delivery/reuse statuses across contract, review writer, validator, and summary logic.
- [ ] Enforce protected-object restrictions and required route justification.
- [ ] Ensure generated routes cannot be justified by missing segmentation capability alone.

## Phase 3 Tasks

- [ ] Tighten validator rules first for generated-route objects, then only later widen if migration coverage is ready.
- [ ] Add final reporting split for clean extraction, approximate reconstruction, generated reconstruction, draft candidates, support-only layers, and blocked objects.
- [ ] Expand tests for planning, capability, generated evidence, and budget boundaries.
- [ ] Run full package validation and quick validation.
- [ ] Review for wording drift across package docs.

## File Ownership Map

### Canonical policy docs

- `docs/superpowers/split-image-assets/design.md`
- `docs/superpowers/split-image-assets/implementation-plan.md`

These define the active design intent and milestone order.

### Package-facing docs

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/pipeline-recipes.md`
- `split-image-assets/references/ui-atomic-split.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/references/confirmation-prompts.md`
- `docs/usage/split-image-assets.md`

### Code ownership hotspots

- `split-image-assets/scripts/check_extraction_environment.py`
- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- shared contract helpers under `split-image-assets/scripts/`

Conditionally touched only if required for clean route integration:

- `split-image-assets/scripts/import_external_assets.py`
- `split-image-assets/scripts/promote_candidate_asset.py`
- `split-image-assets/scripts/compare_candidate_assets.py`
- `split-image-assets/scripts/export_asset_manifest.py`

### Test ownership hotspots

- `split-image-assets/tests/test_skill_package.py`
- any extracted route-planning or generated-delivery focused modules created during this milestone

## Verification Order

Use this order unless a smaller targeted loop is clearly enough for the current phase:

1. targeted tests for the changed route or validator surface
2. broader `split-image-assets` regression
3. package quick validation

When changing rollout-sensitive surfaces, add one more rule:

4. prove at least one legacy-compatible non-generated path still passes unless the phase intentionally migrates it

Do not claim closure from docs alone when the validator or tests still disagree.

## Review Gate

Before milestone closure:

- review package-facing docs for wording drift
- review validator and review-writer changes for truth-surface consistency
- ensure tests cover both honest pass paths and honest failure paths

P0/P1 blockers must be fixed before the milestone is treated as complete.

## Backlog

These are valid future items but are not part of the current milestone unless they become direct blockers:

- built-in generation adapters beyond capability truth surfaces
- richer pilot-template automation
- more granular token accounting per object
- GUI planning or compare surfaces
- reopening the installer UX line as a separate canonical milestone

## Done Definition

This milestone is done only when:

1. planning-first routing is the canonical package story
2. `plan_manifest` is a formal workflow surface
3. `generate` is a formal object route with capability, brief, and evidence rules
4. generated outputs have explicit generated-reconstruction delivery semantics
5. validator and tests reject generated-route dishonesty
6. object-level budget overruns force confirmation
7. final reporting separates route classes clearly
8. rollout-sensitive changes do not silently break legacy-compatible non-generated packages without an explicit migration phase
