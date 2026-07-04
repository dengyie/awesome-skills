# Split Image Assets Current Baseline

Date: 2026-07-04
Status: Canonical current-state implementation baseline for `split-image-assets`
Design source: `docs/superpowers/split-image-assets/design.md`

## Authority

This file is the current implementation baseline, not a historical checklist.
It remains the single implementation plan for the active `split-image-assets` line.

Use it to answer:

- what the package has already shipped
- which milestone just closed
- what the next bounded milestone should be
- which follow-ups are backlog versus active work

If a new milestone starts, update this file in place instead of creating a new dated plan under `docs/superpowers/specs/` or `docs/superpowers/plans/`.

## Current Baseline

The current package baseline is:

- planning-first workflow
- explicit `plan_manifest.json` planning surface
- extraction/generation route separation
- provider bridge contract, registry, and request/result staging surface
- provider bridge default provider selection and low-friction result consumption defaults
- generated-route provider brief and reference-input contract
- generated candidate provider stage evidence reuse
- provider-specific bridge request/result hard validation
- generated compare manifest evidence propagation
- compare-driven promotion orchestration
- provider-aware compare/promotion defaults
- provider-aware generated compare selection
- provider-plan explanation helper
- provider work-item status helper
- candidate work-item status helper
- compare-selected promotion defaults
- candidate promotion approval handoff
- promotion approval runtime guard
- candidate promotion approval auto-record
- compare-to-promotion orchestration adapter
- promotion decision defaults
- single-candidate promotion decision path
- provider-aware candidate lifecycle next steps
- provider-specific candidate approval/promotion resolution
- provider-aware compare command orchestration
- candidate selection recording adapter
- candidate lifecycle orchestration
- candidate lifecycle recommendation variants
- candidate lifecycle schema
- candidate lifecycle task schema
- provider work-item schema
- shared work-item schema helper
- shared task contract
- generated-reconstruction delivery semantics
- decomposed validator architecture
- decomposed test architecture
- generated-route runtime integration for honest pass gating

This means the package is no longer primarily a packaging helper with extraction-adjacent notes. It is now a route-controlled asset workflow with package truth gates.

## Most Recent Closed Milestone

### `registered task bundle helper V1`

Closed status: complete

What landed:

- candidate and provider callers now use `build_registered_task_bundle(...)` instead of composing registry lookup and recommendation bundle assembly by hand
- the registry-aware bundle path is now the normal construction path for known work-item task states

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `shared task registry versioning V1`

Closed status: complete

What landed:

- shared task outputs now expose `task_registry_reference` alongside `task_registry_key` and `task_registry_version`
- helper lookup and real candidate/provider work-item outputs now carry the fuller registry identity surface instead of leaving the registry source implicit

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `work-item recommendation bundle V1`

Closed status: complete

What landed:

- candidate and provider work-item callers now route the final recommendation envelope through `build_recommendation_bundle(...)`
- the shared bundle helper now enforces that the compatibility/default command stays aligned with the default variant path
- provider consume-result recommendations now keep the inferred `--mode` on the compatibility command so the shared bundle consistency rule holds in real outputs
- later follow-up work may continue to move task-goal/default-variant semantics into a shared registry so callers stop repeating those values
- later follow-up work may also route registered task bundle assembly itself through one shared helper so callers stop repeating lookup-plus-bundle wiring

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `shared task contract V1`

Closed status: complete

What landed:

- the shared work-item recommendation surface now has an explicit reference document in `references/shared-task-contract.md`
- main skill/docs surfaces now route readers to the shared task contract instead of forcing them to infer it from helper code
- focused tests now check that the shared contract files and key vocabulary remain present

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `work-item shared schema V1`

Closed status: complete

What landed:

- candidate and provider work-item recommendation builders now reuse a shared `work_item_schema_lib.py` helper for command variants and grouped task envelopes
- the shared helper keeps the candidate/provider task-like recommendation surfaces aligned while preserving the current JSON contract
- later follow-up work may continue to route all three recommendation layers (`recommended_command`, `recommended_command_variants[]`, `recommended_task`) through the same shared bundle helper instead of assembling them separately in each caller

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider work-item schema V1`

Closed status: complete

What landed:

- provider work items now expose `recommended_command_variants[]` and grouped `recommended_task` objects for key bridge states
- prepare-generation-brief, prepare-provider-request, await-provider-result, and consume-provider-result now carry structured provider-bridge task metadata
- the compatibility/default `recommended_command` surface remains intact while richer consumers can read provider-side task grouping directly

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate lifecycle task schema V1`

Closed status: complete

What landed:

- candidate work items now expose a grouped `recommended_task` object when lifecycle branches belong to one task family
- `recommended_command_variants[]` now describes not only branch identity but also written fields and success-state transitions
- compatibility/default command strings remain intact while richer consumers can treat lifecycle recommendations as structured tasks instead of only decorated shell snippets

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate lifecycle schema V1`

Closed status: complete

What landed:

- `recommended_command_variants[]` now carries machine-readable lifecycle metadata such as `phase`, `intent`, branch flag/value, `recommended`, and `requires_fields`
- pending selection and pending promotion approval states now expose structured branch descriptors instead of only label-plus-command rows
- the compatibility/default `recommended_command` surface remains intact while richer consumers can read the schema fields directly

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate lifecycle recommendation variants V1`

Closed status: complete

What landed:

- `describe_candidate_work_items.py` now keeps `recommended_command` for compatibility and also emits `recommended_command_variants[]` for lifecycle states with meaningful explicit branches
- pending compare selection now surfaces explicit `selection-only`, `selection-then-promote-yes`, and `selection-then-decline` variants
- pending promotion approval now surfaces explicit `approve-and-promote` and `decline-promotion` variants instead of hiding the no-path behind chat interpretation

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate lifecycle orchestration V1`

Closed status: complete

What landed:

- `apply_candidate_selection_decision.py` now wraps compare winner selection and can optionally continue into a yes/no promotion decision
- the wrapper reuses `record_candidate_selection.py` first and only then delegates to `apply_candidate_promotion_decision.py`, so the state transition remains explicit instead of skipping selection
- `describe_candidate_work_items.py` now recommends that orchestration wrapper for pending compare-selection states, with `--promotion-answer skip` as the safe default

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate selection recording adapter V1`

Closed status: complete

What landed:

- `record_candidate_selection.py` now provides a low-burden compare-selection adapter that records `selected_candidate_id`, `selection_reason`, and a decision-log entry before approval or promotion
- the adapter shares the same provider-aware compare resolution rules as the later approval and promotion helpers
- `describe_candidate_work_items.py` now recommends the selection adapter whenever compare evidence exists but the selected candidate has not yet been recorded, including single-candidate compare sets

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-aware compare command orchestration V1`

Closed status: complete

What landed:

- `describe_candidate_work_items.py` now recommends compare commands that match the real generated-route provider-aware auto-discovery rules instead of always expanding into a manual candidate list
- single-provider generated pools now get a lower-burden auto-discovery compare command
- mixed-provider generated pools now either reuse a valid explicit plan preference or require an explicit `--provider-id` placeholder instead of silently implying route-default compare is safe

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-specific candidate approval/promotion resolution V1`

Closed status: complete

What landed:

- `record_candidate_promotion_approval.py` can now use `--provider-id` to resolve the correct provider-specific comparison when mixed-provider compare evidence exists for one object
- the same approval adapter can also use `--provider-id` to select the unique staged candidate for that provider when no compare evidence exists yet
- `apply_candidate_promotion_decision.py` now threads that provider-specific resolution through approval and promotion so provider-aware compare paths do not fall back into the direct single-candidate branch by mistake

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-aware candidate lifecycle next steps V1`

Closed status: complete

What landed:

- `describe_candidate_work_items.py` now surfaces staged candidate provider ids and provider-stage manifest paths
- mixed-provider staged candidate pools now say so explicitly before compare instead of staying provider-blind
- candidate lifecycle next-step reporting now carries more of the same provider evidence that later compare/promotion paths depend on

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `single-candidate promotion decision path V1`

Closed status: complete

What landed:

- `record_candidate_promotion_approval.py` now supports the direct single-candidate path when exactly one staged repair candidate exists and no compare evidence exists yet
- `apply_candidate_promotion_decision.py` can now use that same direct single-candidate path for yes/no promotion decisions
- candidate work-item recommendations for the single-candidate pending state now point to a command that actually works on the direct path

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `promotion decision defaults V1`

Closed status: complete

What landed:

- `apply_candidate_promotion_decision.py` can now infer `delivery_class` from planned-route or current object delivery truth in common cases
- the same adapter can now generate a deterministic default `repair_note`
- pending candidate-promotion commands produced by `describe_candidate_work_items.py` no longer need to restate those values when they are safely inferable

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `compare-to-promotion orchestration V1`

Closed status: complete

What landed:

- `apply_candidate_promotion_decision.py` now provides one deterministic command that records a yes/no candidate-promotion decision and, for `yes`, continues directly into promotion
- the adapter reuses compare evidence plus the existing approval adapter and promotion runtime guard instead of inventing a new state surface
- `describe_candidate_work_items.py` now recommends that adapter directly for pending approval states

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate promotion approval auto-record V1`

Closed status: complete

What landed:

- `record_candidate_promotion_approval.py` now records the `candidate_promotion` gate from compare evidence with a lower-burden adapter
- the adapter can reuse compare-owned `selected_candidate_id` and `selection_reason`, or fill the selected candidate from a single-candidate compare set
- `describe_candidate_work_items.py` now recommends that adapter instead of a long raw `record_quality_review.py` command

Verification completed:

- `python -B -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `promotion approval runtime guard V1`

Closed status: complete

What landed:

- `promote_candidate_asset.py` now refuses candidate promotion until `metadata.confirmation.candidate_promotion` is `confirmed` or `not-required`
- promotion runtime guard now agrees with the earlier candidate approval handoff helper instead of letting direct promotion bypass the formal approval gate
- promotion-related test fixtures now explicitly record approval state when they are meant to exercise other validation paths

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate promotion approval handoff V1`

Closed status: complete

What landed:

- `describe_candidate_work_items.py` now distinguishes between “candidate can be promoted” and “candidate promotion approval is still pending”
- when compare has already selected a candidate but `metadata.confirmation.candidate_promotion` is still pending, the helper now recommends a `record_quality_review.py` formal-approval handoff before promotion
- once `candidate_promotion` is confirmed or marked not-required, the helper resumes recommending `promote_candidate_asset.py`

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `compare-selected promotion defaults V1`

Closed status: complete

What landed:

- `promote_candidate_asset.py --comparison-id ...` can now reuse comparison-recorded `selected_candidate_id` and `selection_reason`
- promotion still fails closed when multi-candidate compare evidence has no selected candidate or no recorded selection reason
- candidate work-item recommended promotion commands now omit repeated compare-settled inputs when compare evidence already owns them

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `candidate work-item status V1`

Closed status: complete

What landed:

- `describe_candidate_work_items.py` now writes `_staging/repair_candidates/candidate_work_items.json`
- candidate work items now explain whether candidate stage is empty, compare evidence is needed, a selection is still pending, a candidate is ready for promotion, or candidate work is already complete
- candidate work-item status reuses the existing compare/promotion metadata model instead of inventing a second candidate lifecycle surface
- package docs and tests now describe the candidate work-item status step explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider work-item status V1`

Closed status: complete

What landed:

- `describe_provider_work_items.py` now writes `_staging/providers/provider_work_items.json`
- provider work items now explain whether each object should prepare a generation brief, prepare a provider request, wait for a provider result, or consume a staged result
- work-item status reuses the same provider-selection and consume-mode logic as the existing bridge scripts instead of creating a parallel decision surface
- package docs and tests now describe the provider work-item status step explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-plan explanation V1`

Closed status: complete

What landed:

- `describe_provider_plan.py` now writes `_staging/providers/provider_plan.json` as a package-owned provider-plan summary before broad request generation
- provider selection is now explained per object with route defaults, object-type overrides, valid/invalid plan preferences, selected provider, and alternative provider chains
- provider selection reasoning now reuses the same shared selection logic that `prepare_provider_request.py` uses instead of maintaining a second provider-planning rule set
- package docs and tests now describe the provider-plan summary step explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-aware generated compare selection V1`

Closed status: complete

What landed:

- generated compare auto-discovery now understands provider identity, not just candidate presence
- when multiple generated providers are present, compare auto-discovery now prefers `plan_manifest.provider_preferences.generation_provider_class` and otherwise fails closed
- generated compare manifests now retain provider identity paths for selected-candidate validation
- package docs and tests now describe the provider-aware compare selection path explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-aware compare promotion defaults V1`

Closed status: complete

What landed:

- generated compare can now auto-discover staged candidates with provider-stage evidence for generate-route objects
- generated compare now supplies provider-aware default `review_focus` and `risks` when those values are not provided explicitly
- single-candidate compare-driven promotion can now resolve `candidate_id` and `candidate_asset` from compare evidence without repeating those inputs
- package docs and tests now describe the lower-friction compare/promotion path explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `compare-driven promotion orchestration V1`

Closed status: complete

What landed:

- `promote_candidate_asset.py` can now resolve candidate assets from compare manifests when `--comparison-id` is provided
- generated promotion now prefers compare-manifest candidate evidence before falling back to provider-stage manifests or explicit flags
- generated promotion can now continue from compare evidence even if the sibling stage manifest is no longer present
- package docs and tests now describe the compare-driven promotion path explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `generated compare evidence V1`

Closed status: complete

What landed:

- generated-route compare manifests now carry provider-stage evidence at the candidate-record level
- generated compare now fails closed when provider-stage evidence is expected but missing
- generated direct-promotion compare manifests also preserve that provider-stage evidence
- validator now checks generated compare manifests for selected-candidate provider-stage evidence instead of accepting image-only compare records

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider-specific bridge contract V1`

Closed status: complete

What landed:

- provider request/result validation now checks the selected provider registry entry, not just the generic schema
- request `expected_outputs` must include provider-required outputs
- generate-route request inputs are now provider-required for generation providers
- success/partial provider results now require provider-specific output artifacts
- `external-generated-outputs` request inputs now align to `generation_brief + reference_inputs`

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `generated candidate stage evidence V1`

Closed status: complete

What landed:

- generated `stage-candidate` consumption now writes a sibling provider-stage manifest beside the staged candidate
- that provider-stage manifest carries generation source/model/version plus brief/reference evidence
- `promote_candidate_asset.py` can now reuse that provider-stage manifest to auto-fill generated-reconstruction evidence
- generated-reconstruction promotion now fails closed when neither explicit flags nor provider-stage evidence can satisfy the required generated fields

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `generated-route provider brief contract V1`

Closed status: complete

What landed:

- `prepare_generation_brief.py` now writes package-owned generation briefs plus reference-input manifests under `_staging/generation_briefs/`
- generate-route provider requests now fail closed until those package-owned brief artifacts exist
- `prepare_provider_request.py` auto-attaches `generation_brief` and `reference_inputs` for generate routes once the brief is prepared
- package docs and tests now describe the generated-route bridge input contract explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider result default-consumption V1`

Closed status: complete

What landed:

- `consume_provider_result.py` can now omit `--provider-id` when the staged result is unambiguous or the plan-selected provider is the only safe default
- `consume_provider_result.py` can now omit `--mode` when provider result artifacts expose exactly one consumable path
- extract-style consumption can now reuse the existing metadata object skeleton for role/layer/composition/semantic fields instead of forcing the operator to restate them
- ambiguous staged provider results still fail closed and require explicit `--provider-id`
- package docs and tests now describe the shorter package-owned consume path explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `external-manifest provider consumption V4`

Closed status: complete

What landed:

- `external-professional-outputs` now treats `provider_manifest` as its canonical bridge output
- `consume_provider_result.py --mode import-manifest` can now load `artifacts.provider_manifest` when `--manifest` is omitted
- external-manifest provider docs and usage are aligned to that explicit package-owned bridge path

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

### `provider bridge contract V1`

Closed status: complete

What landed:

- standard provider request/result contract modules
- provider registry and default route chains
- `_staging/providers/<provider-id>/<object-id>/` as the standard bridge staging layout
- deterministic request/result writer scripts for bridge-first upstream execution
- package docs and tests aligned to the provider bridge model
- V1 scope guards: 4 active provider ids only, route default plus object-type override selection, and no direct metadata mutation from provider bridge scripts

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

## Delivered Milestone Ladder

These are the important completed milestones that define the current architecture:

1. contract and QA hardening
2. capability-preflight and confirmation-driven workflow hardening
3. three-layer workflow refactor
4. planning-first generation-routing V1
5. shared package-state consolidation
6. validator decomposition V1
7. test decomposition V1
8. generated-route runtime integration V1
9. provider bridge contract V1
10. provider result default-consumption V1
11. generated-route provider brief contract V1
12. generated candidate stage evidence V1
13. provider-specific bridge contract V1
14. generated compare evidence V1
15. compare-driven promotion orchestration V1
16. provider-aware compare promotion defaults V1
17. provider-aware generated compare selection V1
18. provider-plan explanation V1
19. provider work-item status V1
20. candidate work-item status V1
21. compare-selected promotion defaults V1
22. candidate promotion approval handoff V1
23. promotion approval runtime guard V1
24. candidate promotion approval auto-record V1
25. compare-to-promotion orchestration V1
26. promotion decision defaults V1
27. single-candidate promotion decision path V1
28. provider-aware candidate lifecycle next steps
29. provider-specific candidate approval/promotion resolution V1
30. provider-aware compare command orchestration V1
31. candidate selection recording adapter V1
32. candidate lifecycle orchestration V1
33. candidate lifecycle recommendation variants V1
34. candidate lifecycle schema V1
35. candidate lifecycle task schema V1
36. provider work-item schema V1
37. work-item shared schema V1
38. shared task contract V1
39. work-item recommendation bundle V1
40. shared task registry versioning V1
41. registered task bundle helper V1

Treat these as delivered baseline, not as active checklist items.

## Active P0/P1 Status

There is no currently open `split-image-assets` code milestone.

Current state:

- no active P0 blocker
- no active P1 implementation branch
- current package baseline is verified and published

Any new work should begin by choosing a new bounded milestone on top of the current baseline instead of implicitly continuing the last one.

## Next Recommended Milestones

Choose only one as the next bounded milestone:

1. deeper generated-route provider support
   - more explicit provider capability mapping on top of the now-harder bridge contract
   - richer generated candidate lifecycle helpers on top of prepared briefs, provider-stage evidence, generated compare manifests, compare-driven promotion, provider-aware defaults, provider-aware generated compare selection, provider-plan summaries, provider work-item status, candidate work-item status, compare-selected promotion defaults, candidate promotion approval handoff, promotion approval runtime guard, candidate promotion approval auto-record, compare-to-promotion orchestration, promotion decision defaults, single-candidate promotion decision path, and provider-aware candidate lifecycle next steps
   - optional native runner expansion on top of the bridge layer

2. broader fixture and package migration
   - update older generated fixtures that still rely on package-level `generation_routing`
   - migrate hand-authored packages to the current generated-only pass contract

3. planning-helper depth
   - better planning helpers around route scoring, attempt budgeting, and pilot grouping
   - keep this bounded to planning surfaces, not broad validator expansion

## Out Of Scope Until A New Milestone Is Chosen

Do not reopen these lines by default:

- built-in segmentation runtime hosting
- built-in general image-generation runtime hosting
- broad installer UX work
- unbounded docs rewrite beyond authority cleanup
- large refactors unrelated to route truthfulness or package contract maintenance

## Current Doc Ownership

Use this ownership model when changing the package:

- `design.md`
  - why the workflow is shaped this way
  - invariants
  - route and delivery truth model

- `implementation-plan.md`
  - current baseline
  - last closed milestone
  - next milestone candidates

- `split-image-assets/SKILL.md`
  - agent runtime entrypoint
  - practical workflow and output expectations

- `split-image-assets/references/quick-contract.md`
  - fast truth summary

- `split-image-assets/references/asset-package-contract.md`
  - full validator-facing package contract

- `split-image-assets/references/provider-contract.md`
  - provider bridge request/result contract

- `split-image-assets/references/default-route-chains.md`
  - route default plus object-type override selection rules

- `docs/usage/split-image-assets.md`
  - operator guide

## Acceptance Criteria For The Current Baseline

The package should be treated as healthy only when all of the following remain true:

1. package docs, validator rules, and review-writing rules agree on generated-only pass behavior
2. object-scoped generation-routing evidence is enforced for generated-route objects
3. planning-first route control remains the canonical workflow story
4. the validator and tests stay decomposed by domain rather than collapsing back into monoliths
5. verification remains green on the full `split-image-assets` suite and `quick_validate.py`

## Change Policy For The Next Round

When a new milestone starts:

1. rewrite this file to the new active milestone header
2. keep the delivered baseline summary
3. move the prior active milestone into the delivered milestone ladder
4. do not reintroduce long stale checklists for already completed work
