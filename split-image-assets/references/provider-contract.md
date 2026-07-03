# Provider Contract

Use this file when the workflow needs to connect object routes to a standardized upstream provider surface.

This reference is about the bridge layer between the package workflow and professional upstream tools or generated-output sources. It is not a promise that every provider runs locally inside the skill.

## Goal

Standardize three things before broad native runtime integration:

1. what the workflow asks of a provider
2. what a provider returns
3. how provider requests and results live inside `_staging/`

## Provider Taxonomy

V1 active provider ids are intentionally narrow:

- `external-professional-outputs`
- `external-generated-outputs`
- `codex-controlled-generation`
- `grounded-sam-bridge`

Other provider ideas may exist in backlog or future milestones, but they are not part of the committed V1 provider surface until explicitly promoted.

Supported provider roles:

- `detection`
- `segmentation`
- `matting`
- `reconstruction`
- `generation`

Supported execution modes:

- `bridge`
- `external-manifest`
- `host-managed`
- `native`

`bridge` means the skill creates a normalized request and expects a normalized result, but the upstream execution may happen outside the package.

## Standard Staging Layout

Provider bridge artifacts live under:

```text
_staging/
  providers/
    <provider-id>/
      <object-id>/
        request.json
        result.json
```

Additional provider-owned artifacts may live beside `request.json` and `result.json`, but the canonical request/result manifests should stay at those exact names.

Bridge request/result manifests are staging-only artifacts. They must not write `metadata.json` directly. Final package truth must still be updated only through explicit consumers such as import, compare, promotion, or review adapters.

The standard first consumer is `consume_provider_result.py`. It may:

- turn extract-style provider results into explicit import flow
- turn generate-style provider results into staged candidate flow
- resolve the provider result through explicit `--provider-id`, a single staged result, or the plan-selected default provider when that path is unambiguous
- infer the consume mode from provider result artifacts when the result exposes exactly one consumable artifact set
- for extract-style imports, reuse the existing metadata object skeleton for role/layer/composition/semantic fields when those CLI flags are omitted

It still counts as explicit package-owned consumption, not as direct provider-side metadata mutation.

For `external-manifest` providers, the preferred pattern is:

- provider result records `artifacts.provider_manifest`
- `consume_provider_result.py --mode import-manifest` reads that manifest directly when `--manifest` is omitted

For `generate` routes, the preferred request-side pattern is:

- write `_staging/generation_briefs/<object-id>.json` through `prepare_generation_brief.py`
- write `_staging/generation_briefs/<object-id>_reference_inputs.json` beside it
- let `prepare_provider_request.py` auto-attach those files as `input_refs.generation_brief` and `input_refs.reference_inputs`
- do not allow a generate-route provider request to proceed when those package-owned inputs are missing

For generated candidate staging, the preferred result-side pattern is:

- `consume_provider_result.py --mode stage-candidate` copies the chosen candidate into `_staging/repair_candidates/<object-id>/`
- it also writes `<candidate-id>_provider_stage.json` beside that candidate
- that provider-stage manifest should carry `generation_source`, `generation_model_or_tool`, `generation_version`, `generation_prompt_or_brief_ref`, and `generation_reference_inputs`
- `promote_candidate_asset.py` may reuse that provider-stage manifest to fill generated-reconstruction evidence instead of requiring those flags to be repeated manually

For generated candidate comparison, the preferred compare-side pattern is:

- `compare_candidate_assets.py` should carry provider-stage evidence into the compare manifest candidate records
- generated-route compare candidates should not rely on image-only comparison when provider-stage evidence is expected
- generated delivery that later promotes a selected candidate should keep compare evidence and provider-stage evidence aligned on the same candidate id

## Provider Request Contract

Every provider request should include:

- `schema_version`
- `package_name`
- `provider_id`
- `provider_role`
- `execution_mode`
- `object_id`
- `object_type`
- `planned_route`
- `quality_target`
- `source_image`
- `input_refs`
- `expected_outputs`
- `notes`

`input_refs` should use package-relative paths only.

## Provider Result Contract

Every provider result should include:

- `schema_version`
- `package_name`
- `provider_id`
- `provider_role`
- `execution_mode`
- `object_id`
- `status`
- `artifacts`
- `provenance`
- `warnings`
- `production_ready_hint`
- `next_expected_provider`
- `notes`

`artifacts` should use package-relative paths only.

For `external-manifest` providers, `artifacts.provider_manifest` is the canonical bridge output when the upstream result is a multi-object import manifest rather than a single already-normalized asset pair.

Provider request/result manifests are not valid merely because they are shaped like JSON objects. They must also satisfy the selected provider's registry contract:

- `provider_role` and `execution_mode` must match the provider registry entry
- `planned_route` must be supported by the selected provider
- request `expected_outputs` must include the provider-required outputs
- generate-route requests must include the provider-required brief/reference inputs
- success or partial provider results must include the provider-required output artifacts for that provider class

`provenance` should include:

- `tool_name`
- `tool_role`
- `tool_version`
- `execution_mode`

## Bridge-First Rule

Do not make native model runners the first integration target.

First:

- define the provider request/result contract
- define the provider registry
- define the default route chains
- make external and host-managed providers fit the same request/result surface

Only after that should broad native execution expand.

For V1 specifically:

- keep the active provider set narrow
- prefer one example local bridge plus external/host-managed providers
- do not expand the active surface just because a future provider is easy to name

## Honest Provider Rule

Provider availability does not equal production readiness.

For example:

- a local diffusers runtime is not automatically a production-ready generation provider
- a segmentation bridge is not automatically a production-ready extraction chain unless its outputs can satisfy package QA and validator truth rules

## Default Route Chain Rule

Object routes should default to provider chains, not to free-form tool choice by the agent.

The current default chains are documented in `references/default-route-chains.md`.

Selection rule:

- first choose the route default
- then apply `object_type` override when one is explicitly defined
- then allow `plan_manifest.provider_preferences` to override the default only when the preferred provider is valid for the route
- if no override exists, keep the route default
