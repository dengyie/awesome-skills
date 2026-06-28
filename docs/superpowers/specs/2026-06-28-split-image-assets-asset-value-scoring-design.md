# Split Image Assets Asset Value Scoring Design

Date: 2026-06-28
Status: Proposed and user-approved for spec drafting
Target package: `split-image-assets`

## Goal

Refactor `split-image-assets` so image separation is driven by asset value scoring with an editability-first bias: anything that can be cleanly rebuilt in code or design tools should not be exported as a raster asset by default, while visually fidelity-critical elements should still be eligible for image extraction.

## Problem Statement

`split-image-assets` currently has strong workflow controls for granularity, carrier/glyph separation, candidate promotion, QA review, and interaction gates. However, it still assumes that once an object is identified as a candidate layer, the default outcome is usually some form of image extraction, import, or repair.

That default behavior is too extraction-centric for text-like and rebuildable UI content.

Practical failures caused by the current model:

1. ordinary text, button labels, numeric values, and form values can be treated as image assets too early
2. the skill lacks a first-class scoring layer for deciding whether an object deserves to exist as a raster asset at all
3. complex visual text and decorative typography are not clearly separated from rebuildable text in the package contract
4. high-complexity text-like regions can force the workflow into image extraction without an explicit, auditable “this must remain visual” decision

The desired behavior is stricter:

1. the skill should evaluate asset value before extraction, not after
2. editability should dominate the default decision for ordinary text-like content
3. only fidelity-critical visual text should flow into raster asset extraction by default
4. visually ambiguous text-like regions should route to `requires_user_confirmation` rather than auto-extraction
5. metadata, validator rules, workflow, prompts, and tests should all enforce the same scoring contract

## User-Approved Requirements

The design is based on these confirmed decisions:

1. prioritize editability over raw extraction completeness
2. ordinary text, button labels, numbers, and form values should not be exported as image assets by default
3. logo wordmarks, artistic typography, special outlined text, gradient text, bitmap text effects, and other fidelity-critical visual text may still be exported as image assets
4. when the system detects visually complex, uncertain text-like content, it should prefer `requires_user_confirmation`
5. “high value” in this skill means visual complexity, not product or business importance
6. this skill is responsible for asset splitting decisions, not downstream business semantics

## Scope

This refactor applies only to `split-image-assets`.

In scope:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/tests/test_skill_package.py`
- `docs/usage/split-image-assets.md`

Out of scope:

- OCR extraction, transcription, or text-content understanding beyond lightweight routing classes
- reconstructing live text, code, or design-system output downstream
- adding business-priority scoring
- rewriting the segmentation backend or introducing a new raster extraction engine
- changing unrelated candidate compare, archive, or promotion workflows except where needed to honor the new routing contract

## Non-Goals

This phase should not:

- build a full OCR or semantic text understanding subsystem
- infer exact fonts, kerning, or styles for downstream rebuild
- replace the existing granularity and interaction framework
- decide downstream implementation details for text reconstruction
- introduce a large ML-style scoring model with opaque weights

## Design Principles

The asset value scoring layer should follow these principles:

1. decide whether an object should exist as an image asset before extracting it
2. prefer rebuildability over rasterization when visual fidelity is not the main value
3. treat ordinary text-like UI as rebuild-first by default
4. allow fidelity-critical visual text to stay visual
5. route ambiguity into explicit confirmation rather than silent extraction
6. keep decisions durable, inspectable, and validator-enforced

## Core Decision Model

### Scoring Axes

Each candidate object should be evaluated on three axes before extraction:

- `editability_score`
- `visual_complexity_score`
- `asset_value_score`

### `editability_score`

This score estimates how safely the object can be rebuilt downstream without requiring raster preservation.

High examples:

- plain text
- button labels
- numeric readouts
- form values
- standard badges whose text is not visually stylized

Low examples:

- logo wordmarks
- artistic typography
- text with visual treatment that is inseparable from the design itself

### `visual_complexity_score`

This score estimates how strongly the object depends on visual fidelity that would likely be lost if rebuilt as ordinary live text or basic downstream geometry.

High examples:

- wordmarks with custom forms
- decorative typography
- outlined, gradient, textured, or bitmap-styled text
- stylized text integrated with surrounding artwork

Low examples:

- plain labels
- standard numbers
- editable field content
- ordinary UI copy

### `asset_value_score`

This is the final routing score.

It should not be treated as an independent business metric. It is the decision output derived from editability and visual complexity.

Interpretation:

- high `asset_value_score` means the object is valuable primarily as a visual asset
- low `asset_value_score` means the object is more valuable as rebuildable structure than as pixels

## Routing Outcomes

Each candidate should resolve to one of four actions:

- `extract_asset`
- `rebuild_downstream`
- `requires_user_confirmation`
- `support_only`

### `extract_asset`

Use when the object is visually fidelity-critical and should remain a raster asset.

Expected examples:

- logo wordmarks
- artistic typography
- decorative text effects
- visually inseparable custom text treatments

### `rebuild_downstream`

Use when the object is straightforwardly rebuildable and should not be exported as a formal raster asset.

Expected examples:

- plain text
- button labels
- numeric values
- form values

Behavior:

- do not export a production image asset for the object
- keep a placeholder/object record in metadata for downstream or manual rebuild

### `requires_user_confirmation`

Use when the system detects high visual complexity or uncertainty but cannot safely auto-decide whether the text-like region should remain visual.

This is the approved fallback for ambiguous high-complexity text-like regions.

Trigger conditions include:

- text-like content with strong visual treatment
- partial similarity to a logo wordmark or decorative text
- mixed cases where rebuildability is plausible but visual loss would be meaningful

### `support_only`

Use when the object should remain as structure, context, grouped support, or reference evidence rather than a standalone raster deliverable.

## Text-Like Classification Layer

The scoring model needs lightweight text-specific structure, not full OCR.

Each object may carry:

- `text_role`
- `text_render_class`

### `text_role`

Allowed routing classes:

- `plain-text`
- `button-label`
- `numeric-value`
- `form-value`
- `logo-wordmark`
- `decorative-text`
- `non-text`

### `text_render_class`

Allowed rendering classes:

- `editable`
- `styled-editable`
- `visual-fidelity-critical`
- `non-text`

Interpretation:

- `editable` means downstream reconstruction is the default expected path
- `styled-editable` means editable by default, but the system should inspect whether styling pushes it into ambiguity
- `visual-fidelity-critical` means visual preservation is likely the correct default

## Workflow Integration

The new scoring layer should run before actual image extraction.

Updated high-level workflow:

1. `tooling_preflight`
2. `granularity_alignment`
3. `semantic split plan`
4. `asset_value_scoring`
5. `decision_routing`
6. extraction/import/compare/promotion for objects that still qualify as visual assets

### Asset Value Scoring Stage

Add a formal workflow stage named:

- `Asset Value Scoring Gate`

This is not a universal pause gate.

Behavior:

- it normally runs automatically
- it scores candidate objects and chooses a recommended routing action
- it pauses only when the recommended outcome is `requires_user_confirmation`

### Updated Object Flow

For each candidate object:

1. identify whether it is text-like or non-text
2. assign `text_role` and `text_render_class` when applicable
3. compute `editability_score`, `visual_complexity_score`, and `asset_value_score`
4. assign `recommended_action`
5. resolve `final_action`
6. only route `extract_asset` objects into normal raster extraction

## Confirmation Design

The confirmation system should remain sparse and high-signal.

Do not create a new pause for every text-like object.

Only ask when:

1. the object looks text-like
2. visual complexity is high enough to threaten fidelity if rebuilt
3. the system cannot stably classify it as either ordinary editable text or clearly fidelity-critical visual text

Recommended confirmation question shape:

> “Should this text-like object be rebuilt downstream as editable content, or preserved as a visual asset for fidelity?”

Recommended answers:

- `rebuild_downstream`
- `extract_asset`

Pause category:

- `user-decision`

Metadata effect:

- record scoring summary
- record `recommended_action`
- record `final_action`
- record formal decision-log evidence when confirmation was required

## Metadata Contract Changes

Each object should gain structured routing metadata.

### `value_scoring`

Required fields when the scoring stage runs:

- `editability_score`
- `visual_complexity_score`
- `asset_value_score`
- `scoring_reason`

### `decision_routing`

Required fields:

- `recommended_action`
- `final_action`
- `decision_source`

### `rebuild_intent`

Required fields for text-like or rebuildable objects:

- `rebuildable_downstream`
- `rebuild_notes`

### `text_semantics`

Required for text-like objects:

- `text_role`
- `text_render_class`

## Contract Semantics

The design should explicitly separate recommendation from execution.

### `recommended_action`

The system's scoring result before user override.

### `final_action`

The actual execution route.

Possible outcomes:

- same as recommendation
- overridden after `requires_user_confirmation`

This separation preserves auditability:

- the system may recommend `rebuild_downstream`
- the user may override to `extract_asset`
- the package should retain both facts

## Validator Rules

The validator should enforce the editability-first contract.

### Default Text Rules

Objects classified as:

- `plain-text`
- `button-label`
- `numeric-value`
- `form-value`

must not default directly to `extract_asset` unless one of the following is true:

1. `text_render_class=visual-fidelity-critical`
2. the scoring record explicitly shows high visual complexity justifying visual preservation
3. a formal confirmation record exists that resolved the ambiguity

### Fidelity-Critical Text Rules

Objects classified as:

- `logo-wordmark`
- `decorative-text`

must not silently default to `rebuild_downstream` without scoring evidence that says the visual treatment is safely rebuildable.

### Confirmation Rules

If `recommended_action=requires_user_confirmation`:

1. `final_action` must not remain unresolved in a supposedly completed path
2. the package must contain a formal decision-log record when the object proceeded past the confirmation gate
3. commentary-only notes must not count as confirmation evidence

### Action Consistency Rules

The validator should reject states such as:

1. `rebuild_downstream` with a production-exported visual asset presented as the authoritative output
2. `extract_asset` without scoring evidence explaining why the object is fidelity-critical
3. ordinary editable text routed to extraction without either complexity evidence or user confirmation
4. `requires_user_confirmation` objects advancing without formal decision evidence

## Documentation Changes

### `SKILL.md`

Add:

- editability-first asset value scoring policy
- ordinary text defaulting to rebuild, not raster export
- visually complex text-like ambiguity routing to `requires_user_confirmation`

### `references/workflow.md`

Add:

- `Asset Value Scoring Gate`
- object routing sequence before extraction
- text-like routing rules

### `references/confirmation-prompts.md`

Add:

- prompt template for text-like ambiguity
- explicit “do not ask for ordinary text defaults” guidance

### `references/asset-package-contract.md`

Add:

- object scoring metadata schema
- routing metadata schema
- text semantics schema

### `docs/usage/split-image-assets.md`

Add:

- user-facing explanation that text-like content is evaluated for downstream rebuild before raster extraction
- explanation that ordinary editable text is not exported as an image asset by default

## Tests

Minimum new regression themes:

1. ordinary text routes to `rebuild_downstream`
2. fidelity-critical decorative or wordmark text can route to `extract_asset`
3. visually ambiguous text-like objects route to `requires_user_confirmation`
4. invalid text/action combinations fail validation
5. `requires_user_confirmation` objects need formal decision evidence before final routing completes

## Acceptance Criteria

The refactor is complete only when all of the following are true:

1. the workflow scores candidate objects before extraction
2. ordinary editable text defaults to non-raster downstream rebuild behavior
3. fidelity-critical text can still be preserved as raster assets
4. visually complex ambiguous text-like objects route to `requires_user_confirmation`
5. object metadata records scoring, routing, and text semantics in a durable way
6. validator rules reject illegal extraction/rebuild combinations
7. package tests catch regressions back to text-first auto-extraction behavior

## Review Checklist

Before implementation planning begins, verify that:

1. business importance is not part of the scoring model
2. visual complexity is the main ambiguity trigger
3. ordinary text-like content is rebuild-first by default
4. fidelity-critical text remains eligible for raster extraction
5. ambiguous high-complexity text-like objects pause only through `requires_user_confirmation`
6. metadata and validator rules preserve the recommendation versus final action split
