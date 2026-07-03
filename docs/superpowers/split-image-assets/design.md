# Split Image Assets Unified Planning-First Design

Date: 2026-07-03
Status: Canonical design for ongoing `split-image-assets` development
Target package: `split-image-assets`

## Authority

This is the single governing design document for the current `split-image-assets` line.

It replaces the prior installer-UX-first canonical design as the active authority for this package.

If a lower-level doc, package reference, script default, or test expectation conflicts with this document, this document wins and the implementation should be brought back into alignment.

## Goal

Refactor `split-image-assets` into a planning-first asset workflow with five properties:

1. the workflow plans the whole image before spending extraction or generation effort
2. each object is routed explicitly to the cheapest truthful path
3. generation is a first-class but tightly constrained workflow path, not a silent fallback
4. generated outputs may be delivered only under explicit generated-reconstruction semantics
5. package metadata, validator rules, compare evidence, and final reporting all enforce the same truth claims

This is not a new segmentation engine project. It is a workflow-control, contract, and product-truth redesign for the existing package.

## Problem Statement

`split-image-assets` is already strong on package rigor:

- it distinguishes structural validation from visual quality
- it records formal review state in metadata
- it has deterministic preview, audit, validation, compare, promotion, and manifest tooling
- it has strong honesty rules around approximate reconstruction
- it already treats professional upstream extraction as the normal production path

However, the current package still has four systemic problems.

### 1. It spends effort too late

The workflow still lets an agent spend segmentation, cleanup, compare, and review effort before a whole-image plan decides which objects are even worth extracting.

This causes:

- avoidable token waste
- repeated failed cleanup loops
- extraction work on objects that should have been rebuilt or generated

### 2. It does not yet formalize generation as a constrained route

The package already knows how to remain honest about approximate reconstruction, but it does not yet define a formal object route for cases where continued extraction is economically or visually inferior to constrained generation.

Without that route:

- agents keep pushing segmentation too far
- generated fixes would be under-specified
- users cannot see early enough when the task changed from extraction to reconstruction

### 3. It still mixes route planning and final asset state too loosely

`metadata.json` is currently the main truth surface, but the package does not yet separate:

- whole-image route planning
- object-level generation constraints
- final package state

This makes the workflow harder to audit and easier to drift.

### 4. It lacks an explicit budget and escalation model for expensive objects

The current workflow can still keep trying one object too many times without a formal object-level attempt budget and route-switch confirmation boundary.

## User-Confirmed Requirements

The design is based on these explicit decisions from the current thread:

1. the workflow should start with whole-image planning
2. route planning should aggressively divert bad extraction candidates before they burn too much token budget
3. generation must be triggered by combined judgment, not by visual difficulty alone
4. the combined trigger should use four lightweight route signals:
   - `recoverability_low`
   - `object_is_reconstruction_like`
   - `quality_target_high`
   - `segmentation_cost_unfavorable`
5. default route thresholds should be:
   - `3/4`: recommend `generate`
   - `2/4`: require user confirmation
   - `0-1/4`: continue non-generation path
6. `generate` must be a distinct route from `reconstruct`
7. `generate` outputs must not silently claim clean extraction semantics
8. `generate` outputs may be deliverable, but only under explicit generated-reconstruction labeling
9. route-to-generate must not be caused merely by missing local segmentation tooling
10. objects routed to `generate` must record why extraction and reconstruction were not chosen
11. `generate` should default to object-level reference-constrained generation, not free redraw
12. the workflow may skip formal extraction for high-confidence generate objects after planning, but only after an object-level confirmation
13. every generate object must have a generation brief before generation begins
14. generate should default to two candidates and one generation round
15. failed generate attempts must not auto-loop; the workflow must branch explicitly
16. the package should support pilot-first reuse for batches of similar objects
17. object-level attempt budgets must be explicit, and budget overruns must force confirmation
18. ordinary UI text should default to `rebuild_downstream`
19. large background or support plates should default to `support_only` or approximate support delivery, not atomic asset promotion
20. the default workflow must forbid whole-image redraw followed by re-cutting
21. generation must have its own capability gate
22. generation capability must distinguish `installed`, `runtime_ready`, and `production_ready`
23. generation `production_ready` requires object-level transparent asset delivery, not just ordinary image generation
24. final reporting must separate clean extraction, approximate reconstruction, generated reconstruction, draft candidates, support-only layers, and blocked objects
25. `generated-reconstruction` must have a stronger evidence package than ordinary approximate reconstruction

## Scope

In scope for the current active line:

- `docs/superpowers/split-image-assets/design.md`
- `docs/superpowers/split-image-assets/implementation-plan.md`
- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/pipeline-recipes.md`
- `split-image-assets/references/ui-atomic-split.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/references/confirmation-prompts.md`
- `docs/usage/split-image-assets.md`
- `split-image-assets/scripts/check_extraction_environment.py`
- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- package-local planning and generation-routing helpers
- tests needed to enforce the new route contract

Conditionally in scope only when required for truthful alignment:

- `split-image-assets/scripts/import_external_assets.py`
- `split-image-assets/scripts/promote_candidate_asset.py`
- `split-image-assets/scripts/compare_candidate_assets.py`
- `split-image-assets/scripts/export_asset_manifest.py`

Out of scope:

- turning this package into a built-in segmentation model host
- turning this package into a free-form image-generation product
- allowing generated results to masquerade as clean extraction
- whole-image redraw workflows as the default decomposition strategy
- relaxing existing honesty gates around approximate reconstruction

## Active-Line Disposition

The earlier contract-hardening line remains preserved baseline behavior.

The earlier installer UX line remains useful backlog, but it is not the active milestone now.

For this design:

- contract-hardening behavior remains required baseline
- installer UX ideas may still be reused where they help capability truthfulness
- planning-first route control and generated-reconstruction discipline are the delivered baseline
- no new active milestone is open until a new bounded follow-up is explicitly chosen

This means the canonical design remains planning-first, but the implementation line should now be read through the shipped-baseline model in `implementation-plan.md` rather than through an in-flight milestone checklist.

## Non-Goals

This redesign should not:

- reduce the skill to a casual prompt
- hide route ambiguity inside informal commentary
- let missing segmentation tooling silently trigger generation
- let generated outputs satisfy `production-ready` extraction semantics
- allow repeated object retries without budget control
- default to whole-image redraw and post-cut extraction
- promote generated objects from package-level final acceptance alone

## Design Principles

1. Plan the whole image before spending expensive work.
2. Route each object to the cheapest truthful path.
3. Generation is allowed only as a constrained, auditable route.
4. Commentary is never a route decision.
5. Object-level truth claims must stay object-level.
6. Attempt budgets define agent autonomy boundaries.
7. Batch reuse is allowed only after a pilot proves the route.
8. Generated delivery must stay visibly different from extraction delivery.

## Workflow Architecture

The workflow now has four major layers:

1. capability preparation
2. whole-image planning
3. object-route execution
4. quality adjudication

### 1. Capability Preparation

The workflow must inspect both:

- segmentation capability
- generation capability

Each capability surface must distinguish:

- `installed`
- `runtime_ready`
- `production_ready`

Generation capability must not be treated as `production_ready` unless it can support:

- recognized generation source
- object-level constrained generation
- transparent deliverable assets
- traceable candidate evidence

### 2. Whole-Image Planning

Before extraction or generation begins, the workflow must create a package-owned `plan_manifest`.

The plan stage decides:

- which objects are worth raster effort at all
- which route each object should follow
- which objects can share a pilot/template workflow
- what the attempt budget is for each object

No formal extraction, reconstruction, or generation should begin before this plan exists.

### 3. Object-Route Execution

Every object must resolve to one of:

- `extract`
- `reconstruct`
- `generate`
- `rebuild_downstream`
- `support_only`

### 4. Quality Adjudication

The workflow must continue to separate:

- structural validation
- visual audit warnings
- object-level promotion approval
- package-level final acceptance

Generation does not bypass these layers. It must integrate into them.

## Compatibility Strategy

This redesign is not allowed to create two competing truth surfaces during rollout.

The package already has stable metadata, validator, and review-writer behavior. The planning-first route model must therefore land through an explicit compatibility strategy rather than an abrupt semantic replacement.

Three compatibility surfaces must be kept explicit during implementation:

1. route compatibility
2. delivery-state compatibility
3. validator rollout compatibility

### Route Compatibility

The new planning-first route taxonomy is:

- `extract`
- `reconstruct`
- `generate`
- `rebuild_downstream`
- `support_only`

The current package-owned routing taxonomy already stored in object metadata is:

- `extract_asset`
- `rebuild_downstream`
- `requires_user_confirmation`
- `support_only`

The new route taxonomy is therefore a planning taxonomy first, not an immediate replacement for every existing object-state field.

#### Mapping Rule

During rollout:

| `planned_route` | Current object-state expectation |
| --- | --- |
| `extract` | `decision_routing.final_action=extract_asset` |
| `reconstruct` | `decision_routing.final_action=extract_asset` plus explicit reconstruction-oriented delivery fields |
| `generate` | `decision_routing.final_action=extract_asset` only after generated-object approval; before that, the route remains a planning-state truth and must not be mistaken for ordinary extraction |
| `rebuild_downstream` | `decision_routing.final_action=rebuild_downstream` |
| `support_only` | `decision_routing.final_action=support_only` |

`requires_user_confirmation` remains a current object-state action, not a long-lived planning route. In the new model it is the unresolved execution result of a planning branch, not one of the five target routes.

This means:

- `planned_route` lives primarily in `plan_manifest`
- `decision_routing` remains the current execution-state reflection inside `metadata.json`
- implementation must not silently replace `decision_routing.final_action` with raw `planned_route` strings until the broader contract is intentionally migrated

### Delivery-State Compatibility

The package already has live `delivery_class`, `reuse_status`, and `qa.status` semantics.

The new planning-first design adds generated-delivery truthfulness, but it must not break all existing pass gates in one step.

#### Compatibility Matrix

During rollout, use this matrix:

| Visual truth class | `delivery_class` | `reuse_status` | Pass-supporting meaning |
| --- | --- | --- | --- |
| clean extracted asset | `clean-extraction` | `production-ready` | existing clean extraction path |
| accepted approximate repair | `approximate-reconstruction` | `accepted-approximate-reconstruction` (target) or temporary legacy-compatible approximation state during migration | accepted non-clean extraction |
| accepted generated object | `generated-reconstruction` | `accepted-generated-reconstruction` | accepted generated delivery, never plain clean extraction |
| staged candidate | `draft-candidate` | `draft-candidate` | non-final candidate only |
| support layer | `support-only` | `support-only` | non-atomic support delivery |

#### Migration Rule

The implementation must not introduce new generated or approximation statuses without also updating:

- the shared contract constants
- review-writer pass gates
- validator pass gates
- asset summary counting
- downstream manifest export rules

Until those five surfaces are aligned, a new status is only a design target, not a shippable code change.

### Validator Rollout Compatibility

`plan_manifest` is a hard design target, but validator rollout must be staged.

The package currently has many metadata-first fixtures and real packages. Immediate global hard-failure on missing `plan_manifest` would create avoidable breakage.

#### Required Rollout Stages

1. `plan_manifest` exists as a formal surface and may be generated by helpers.
2. `generate` route objects require `plan_manifest`.
3. new packages created after the rollout require `plan_manifest`.
4. only after migration coverage is ready may validator rules consider broader universal enforcement.

This staged rollout is mandatory. Do not make `plan_manifest` an unconditional global validator hard-failure in the first code pass.

## Canonical Gates

The package continues to use conservative continuous execution.

The default state is `Running`. Stops are still limited to:

- `user-decision`
- `external-blocker`
- `formal-approval`

The normalized gates now include one new formal gate:

| Gate | Stop class | State | Meaning |
| --- | --- | --- | --- |
| `tooling_preflight` | `external-blocker` | `AwaitingExternalBlocker` | choose or unblock a truthful capability path |
| `granularity_alignment` | `user-decision` | `AwaitingDecision` | settle split scope and downstream rebuild boundaries |
| `generation_routing` | `user-decision` | `AwaitingDecision` | settle object routes when the generate threshold is ambiguous |
| `pilot_object` | `formal-approval` | `AwaitingApproval` | approve widening a dense or high-cost batch |
| `approximate_reconstruction` | `user-decision` | `AwaitingDecision` | accept or reject approximate visual truth claims |
| `candidate_promotion` | `formal-approval` | `AwaitingApproval` | replace the current owned object revision |
| `final_acceptance` | `formal-approval` | `AwaitingApproval` | approve final package claim level |

### `generation_routing`

This is the new planning-era gate.

It is triggered when:

- an object scores `2/4` on the generate route signals
- a route switch would materially change downstream truth claims
- the object falls into a protected class and requires explicit user permission

It should not be used when:

- the route is already obvious from the plan rules
- the object scores `0-1/4` or `3/4` and no protected-object policy blocks progress

## Plan Manifest Contract

The package now requires a pre-execution planning surface separate from `metadata.json`.

`plan_manifest` is the route-planning truth surface.

It should record, at minimum, for each object:

- `object_id`
- `object_type`
- `planned_route`
- `route_signals`
- `route_score`
- `route_reason`
- `needs_user_confirmation`
- `quality_target`
- `attempt_budget`
- `token_budget_hint`
- `pilot_group`
- `promotion_requirement`
- `attempts_used`
- `attempt_history`
- `protected_policy`
- `protected_approval_required`
- `protected_approval_ref`

For `generate` objects, it must also record:

- `why_not_extract`
- `why_not_reconstruct`
- `why_generate`
- `risk_note`

`attempt_budget` and `token_budget_hint` are not enough by themselves for validator-visible honesty. The plan surface must also be able to show whether the object stayed within budget, exceeded budget, or switched routes after confirmation.

`metadata.json` remains the final package-state surface. It must not absorb the entire planning surface.

## Generation Brief Contract

Every object routed to `generate` must have a package-owned generation brief before generation begins.

The brief should record at minimum:

- `object_id`
- `object_type`
- `source_crop`
- `rough_localization`
- `rough_mask`
- `neighbor_context`
- `style_constraints`
- `must_keep`
- `must_avoid`
- `target_transparency`
- `intended_delivery_class`
- `why_not_extract`
- `why_not_reconstruct`
- `why_generate`
- `risk_note`

The default generation target for reusable objects is a tight transparent PNG.

Whole-image redraw followed by object recutting is prohibited as the default route.

## Generation Provider Contract

Generation capability must use named provider classes rather than vague tool presence.

At minimum, the design recognizes these provider classes:

- `codex-controlled-generation`
- `external-generated-outputs`
- `local-model-runtime`

These provider classes are execution-source classes, not quality promises by themselves.

### Provider Readiness Rule

Each provider class must still be evaluated as:

- `installed`
- `runtime_ready`
- `production_ready`

`production_ready` requires all of:

- recognized provider class
- object-level constrained generation workflow
- transparent asset delivery path
- durable evidence capture suitable for compare, promotion, and final reporting

Raw image generation availability is not enough.

## Route Decision Model

### Generate Route Signals

The package must use four lightweight signals:

- `recoverability_low`
- `object_is_reconstruction_like`
- `quality_target_high`
- `segmentation_cost_unfavorable`

Default routing thresholds:

- `3/4`: recommend `generate`
- `2/4`: require user confirmation
- `0-1/4`: continue non-generation path

### Protected Objects

These objects must not route to `generate` by default without explicit permission:

- primary brand logos
- highly recognizable hero mascots or hero illustrations
- legally or brand-sensitive identity marks
- objects that must remain faithful to original source pixels

The plan surface must record both the protected-object classification and the approval reference when the route is overridden.

### Default Non-Generate Rules

- ordinary text, labels, values, and button copy default to `rebuild_downstream`
- large background plates, support plates, and contextual repair surfaces default to `support_only` or approximate support delivery
- `generate` must not be chosen merely because segmentation tooling is unavailable

## Reconstruct Versus Generate

The package must distinguish these routes formally:

- `reconstruct`: still primarily constrained by recoverable source structure
- `generate`: source-informed but no longer a pure extraction or local repair task

These are not the same truth class and must not share the same final delivery labels.

## Candidate, Budget, And Retry Policy

For generated routes:

- default to one generation round
- default to two candidates
- do not auto-loop retries

If generation does not succeed:

1. `leave-needs-review`
2. `retry-generate`
3. `fallback-to-reconstruct`

Object-level attempt budgets must be recorded in `plan_manifest`.

When an object exceeds its budget:

- the agent must not silently continue
- the agent must not silently change route
- the workflow must return to explicit confirmation

Validator-visible budget honesty depends on recorded attempt use. Budget fields without attempt-use tracking are insufficient.

## Batch Reuse Model

When many objects share the same route shape, the package may use:

- one pilot object
- one full pilot brief
- sibling delta briefs
- a shared batch compare context

However:

- every object still needs its own candidate identity
- every object still needs its own selection reason
- every object still needs its own promotion approval

Batch reuse is an execution optimization, not a truth-surface shortcut.

## Delivery Semantics

The package must keep generated delivery visibly separate from extraction delivery.

### Delivery Classes

The package must distinguish:

- `clean-extraction`
- `approximate-reconstruction`
- `generated-reconstruction`

### Reuse Status

The package must distinguish:

- `production-ready`
- `accepted-approximate-reconstruction`
- `accepted-generated-reconstruction`

Generated objects must never be reported as plain `production-ready` extraction assets.

Implementation note: introducing `accepted-approximate-reconstruction` or `accepted-generated-reconstruction` in code is a coordinated contract migration, not a doc-only rename. These statuses must not land piecemeal.

## Generated-Reconstruction Evidence Contract

Generated delivery is allowed only with a stronger evidence surface.

For any object delivered as `generated-reconstruction`, the package must retain:

- `generation_source`
- `model_or_tool`
- `version`
- `prompt_or_brief_ref`
- `reference_inputs`
- `candidate_id`
- `compare_evidence`
- `promotion_acceptance`
- `selection_reason`

This evidence is not optional documentation. It is part of the formal truth surface.

## Promotion And Acceptance Rules

Generated objects must pass through:

1. object-level compare
2. object-level promotion approval
3. package-level final acceptance

Package-level final acceptance must not silently imply that a generated object was accepted.

Generated objects must be approved object-by-object before the package may claim final delivery.

## Validator Requirements

The validator must enforce at least the following:

- staged rollout for `plan_manifest`:
  - missing `plan_manifest` is initially a hard failure only for generated-route objects
  - broader enforcement is allowed only after helper, fixture, and migration coverage exist
- `generate` objects must record route reasoning fields
- generated delivery must use `delivery_class=generated-reconstruction`
- accepted generated delivery must use generated-specific reuse semantics
- generated delivery must retain its evidence contract
- missing segmentation capability must not by itself justify a generated delivery claim
- protected objects must not reach generated delivery without explicit permission evidence
- budget overrun paths must not look like ordinary successful first-path completion

The validator should continue to check truthfulness, not aesthetics.

## Final Reporting Contract

Final reporting must separate:

- `clean extracted assets`
- `accepted approximate reconstructions`
- `accepted generated reconstructions`
- `draft candidates`
- `support-only layers`
- `blocked / needs-review objects`

This reporting split is required because one package may now contain truthful outputs from multiple route classes.

## Architecture Requirements

The next implementation phase should favor small, explicit ownership surfaces:

1. shared route and delivery enums in a package-local contract module
2. plan-manifest helpers separated from final metadata mutation helpers
3. generation-capability logic separated from segmentation-capability logic but expressed in the same capability vocabulary
4. validator decomposition so generated-delivery checks do not become ad hoc branches
5. tests grouped around route planning, generated delivery, and budget control

## Success Criteria

The redesign is successful when all of the following are true:

1. the canonical design and implementation plan both describe planning-first routing
2. the package cannot silently begin expensive extraction before whole-image planning
3. `generate` is a formal route with its own gate, capability model, brief, and evidence package
4. generated outputs can be delivered honestly without pretending to be extraction
5. budget overruns force confirmation instead of silent retries
6. batch reuse lowers cost without weakening object-level truth claims
7. tests and validator rules fail on generated-route contract drift
