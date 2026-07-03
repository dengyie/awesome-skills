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

It still counts as explicit package-owned consumption, not as direct provider-side metadata mutation.

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
- if no override exists, keep the route default
