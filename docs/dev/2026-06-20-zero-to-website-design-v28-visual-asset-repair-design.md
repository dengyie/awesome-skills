# V28 Zero-To-Website Visual Asset Repair Design

## Purpose

This document designs the next repair pass for `zero-to-website-design` after V27.

The asset is important because it is not only a set of instructions. It is a reusable control system for preventing visually driven website work from becoming vague, screenshot-based, generic, or overclaimed. The next pass should turn the hard-earned details into a stronger, more coherent asset model.

## Current Baseline

V27 already added:

- concrete user-selected visual authority before `Visual Delivery Ready`
- Reference-To-DOM Map
- component-slot raster asset rules
- component-slot prompt records
- top 3 visible differences after each visual pass
- visual usability gate
- user-feedback status updates
- final visual pass report

This is the right direction, but the rules are still distributed across existing references. A future agent may follow the words without understanding the underlying model.

## New Problem Statement

The next failure mode is not just "agent forgot a checklist item." It is model drift across five asset layers:

1. Visual authority: which image or page capture is allowed to control the route.
2. Region mapping: which reference regions become DOM, CSS, local assets, or accepted gaps.
3. Asset production: which local/generated/sourced assets are allowed and what slot they occupy.
4. Visual correction: which visible differences drive the next edit pass.
5. Delivery claim: what status can honestly be reported to the user.

If these layers are not connected, the agent can still produce a site that passes tests but fails the user's eye.

## Concrete Issue Found During Review

`zero-to-website-design/references/design-fidelity-loop.md` contains mojibake in the user-feedback examples. This is a direct example of the new gate catching a real problem:

- Text encoding is part of visual delivery.
- Example text inside the skill itself must not demonstrate a broken delivery state.
- Non-ASCII examples in skill references need either correct UTF-8 preservation or ASCII-safe paraphrases.

The V28 repair should remove the corrupted examples and replace them with ASCII-safe wording or correctly encoded text only where necessary.

## Design Principle

Treat a visually driven website as an asset graph, not as a page screenshot.

Every visible thing in the selected reference must move through this chain:

```text
visual authority
-> reference region
-> implementation owner
-> asset slot or DOM component
-> evidence screenshot
-> difference status
-> delivery claim
```

No node in the chain may be implicit when the route is used to claim `Visual Delivery Ready`.

## Proposed V28 Scope

### P0/P1

- Add a dedicated `references/visual-asset-pipeline.md` reference.
- Route to it from `SKILL.md` when a binding route uses generated, sourced, drawn, or local visual assets.
- Repair mojibake in existing references.
- Strengthen templates so asset slots, implementation ownership, and evidence status can be tracked together.
- Add regression tests for:
  - visual asset pipeline reference exists and is routed
  - no mojibake tokens remain in `zero-to-website-design` docs
  - asset slots include ownership, text policy, perspective policy, and evidence path
  - final delivery status follows weakest visual asset status

### Out Of Scope

- No automated image-diff script in this pass.
- No new image generation assets.
- No migration of old project docs.
- No new frontend implementation.

## Visual Asset Pipeline Contract

The new reference should define these states.

### Asset Authority State

- `candidate`: visible option, not selected
- `approved-direction`: selected style or route direction
- `binding-route`: controls final route composition
- `temporary-binding`: controls this milestone but needs later replacement
- `component-slot`: local/generated/sourced asset that fills one mapped region
- `obsolete`: replaced or rejected

### Implementation Owner State

Each mapped reference region must have one owner:

- `dom-owner`: real layout, text, link, control, chart, form, table, or component
- `css-owner`: primitive shape, stroke, shadow, texture, layout decoration, or responsive crop
- `asset-owner`: local/generated/sourced raster/vector asset in a defined component slot
- `accepted-gap`: explicitly not implemented for this milestone

No region can be `unowned`.

### Asset Slot State

Each generated/sourced/local component-slot asset must record:

- route
- section
- reference region
- owner component
- target size or aspect ratio
- crop and safe-padding rules
- must-match list
- must-avoid list
- text policy
- perspective/tilt policy
- source method
- output path
- evidence screenshot path
- replacement trigger
- current status

### Text Policy

Use these values:

- `no-text`: asset must not contain readable text
- `ornamental-text-only`: visual marks are allowed but not readable content
- `real-dom-text-required`: all readable text must be DOM text
- `baked-text-approved`: readable text may be baked only when explicitly approved and not required for accessibility, SEO, localization, or interaction

Default should be `real-dom-text-required` for UI, navigation, labels, cards, and content.

### Perspective/Tilt Policy

Use these values:

- `css-applied`: image is front-facing; perspective, tilt, rotation, or shadow is applied in CSS
- `asset-baked`: perspective is part of the asset
- `mixed-with-reason`: both are used and the reason is recorded

Default should be `css-applied` for reusable UI panels and cards.

## Difference-Driven Repair Loop

The current Top 3 rule should become more operational.

Each visual pass should record:

```text
Visual pass:
- Reference:
- Implementation screenshot:
- Top 3 visible differences:
  1.
  2.
  3.
- Fix selected for this pass:
- Why this fix is highest value:
- Evidence after fix:
- Status after fix:
```

Rules:

- Do not start another broad edit until the top 3 are named.
- The next edit must address at least one named difference.
- If a named difference is not fixed, it must be moved to `accepted-gap` with reason.
- New screenshots replace old proof. Old screenshots can remain as history, not final evidence.

## User Feedback State Machine

User feedback should update route state:

```text
not-matching -> blocked-visual
must-be-interactive -> blocked-p0-screenshot-guard
selected-this-direction -> approved-direction
use-this-as-reference -> binding-route or temporary-binding
this-is-deliverable -> close-enough
ship-it -> final review gate, not automatic Visual Delivery Ready
```

Important: positive user feedback can narrow the remaining work. It must not erase required build, browser QA, text encoding, real DOM, or asset evidence.

## First-Viewport Composition Gate

For homepages and landing pages, the route should have a separate first-viewport record:

- binding reference viewport
- implementation viewport
- dominant visual system
- primary content block position
- next-section exposure
- whether lower sections compete with hero
- whether decorative sections push primary content down
- status: `matched`, `accepted-gap`, `blocked`

This should live in the QA template because it is an acceptance concern, not just a design note.

## Mojibake And Text Encoding Repair

V28 should treat mojibake as both:

- content correctness failure
- visual delivery failure

Proposed rule:

```text
If any visible UI text, final report text, or skill reference example is mojibake, the route or package cannot be considered delivery-ready.
```

Implementation detail:

- Prefer ASCII paraphrases in skill docs when exact non-English examples are not required.
- If non-English examples are useful, keep files UTF-8 and add regression tests for the exact expected text or for absence of common mojibake tokens.
- Add tests against obvious mojibake fragments in `zero-to-website-design` docs.

## Template Changes

### Implementation Plan

Add:

```md
## Visual Asset Pipeline

| Route | Reference Region | Implementation Owner | Asset Slot | Text Policy | Perspective/Tilt Policy | Evidence Path | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

### QA Report

Add:

```md
## Visual Asset Evidence

| Route | Asset Slot | Output Path | Source Method | Evidence Screenshot | Text Policy Pass | Perspective Policy Pass | Replacement Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

### Final Visual Pass Report

Add:

```md
- Visual asset pipeline status:
- First-viewport composition status:
- Mojibake/text encoding status:
- User feedback state:
```

## Regression Test Design

Add a new test such as:

```python
def test_visual_asset_pipeline_contract_is_required(self):
    ...
```

Assertions should cover:

- `visual-asset-pipeline.md` exists
- `SKILL.md` routes to it
- implementation and QA templates include visual asset pipeline tables
- production delivery mentions visual asset pipeline status
- docs include text policy and perspective/tilt policy

Add another test:

```python
def test_zero_to_website_docs_do_not_contain_mojibake(self):
    ...
```

Scan `SKILL.md`, `references/*.md`, `assets/templates/*.md`, and `docs/usage/zero-to-website-design.md` for common mojibake fragments.

## Completion Criteria

V28 should stop when:

- the new visual asset pipeline contract exists
- mojibake is repaired
- templates capture asset evidence
- package tests pass
- skill validation passes
- production review finds no P0/P1 blocker
- local installed skill is synced if the change is published

## Expected Outcome

After V28, `zero-to-website-design` should make the agent think in asset ownership and evidence flow:

- Which image is authoritative?
- Which region does this visual thing come from?
- Is it DOM, CSS, asset, or accepted gap?
- If it is an asset, what slot owns it?
- Can the user inspect the latest screenshot?
- What are the top visible differences?
- What status is honest?

That is the durable behavior this asset needs.
