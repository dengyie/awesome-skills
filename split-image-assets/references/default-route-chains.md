# Default Route Chains

Use this file when a planned object route needs a default upstream provider chain.

These defaults are not hardcoded quality guarantees. They are the standard first-choice orchestration path so the agent does not rebuild the same tool-selection logic every run.

V1 active provider surface is intentionally limited to:

- `external-professional-outputs`
- `external-generated-outputs`
- `codex-controlled-generation`
- `grounded-sam-bridge`

This file should not be read as approval to broaden the active provider set beyond those four ids during V1.

## Route: `extract`

Default chain:

1. `grounded-sam-bridge`

Object-type overrides:

- `photo-object-matte` -> `external-professional-outputs`
- `outlined-illustration-logo` -> `external-professional-outputs`

Fallback:

- `external-professional-outputs`

## Route: `reconstruct`

Default chain:

1. `external-professional-outputs`

## Route: `generate`

Default chain:

1. `codex-controlled-generation`

Fallbacks:

- `external-generated-outputs`

Generated delivery still requires compare, promotion, and acceptance evidence before final pass claims.

## Route: `rebuild_downstream`

Default chain:

- no raster provider chain
- record rebuild intent
- keep placeholder metadata and downstream rebuild semantics

## Route: `support_only`

Default chain:

- no atomic production provider chain
- keep grouped/support delivery honest

## Selection Rule

Use the default chain unless one of these is true:

- preflight proves the default provider is unavailable
- the object type requires a different specialized provider
- the user has already confirmed a different provider path
- a provider-specific restriction blocks the default chain

This is a two-step rule:

1. route default
2. object-type override when explicitly defined

`prepare_provider_request.py` should be able to use this rule without requiring an explicit `--provider-id` on every invocation.
