# Visual Asset Pipeline

Use this reference when a binding route uses generated, sourced, drawn, or local visual assets.

The purpose is to keep visual assets connected to route authority, DOM ownership, implementation evidence, and final readiness claims. A visual asset is not just an image file; it is a controlled node in the website delivery chain.

Read `resource-atomicity.md` before generating, sourcing, drawing, extracting, or saving asset files for a binding route. This pipeline controls readiness state; resource atomicity controls file boundaries.

## Core Chain

Every visible asset-controlled region in a binding reference must move through this chain:

```text
visual authority
-> reference region
-> implementation owner
-> resource unit
-> asset slot or DOM component
-> evidence screenshot
-> difference status
-> delivery claim
```

No node in this chain may be implicit when the route supports `Visual Delivery Ready`.

## Asset Authority State

Use these states:

- `candidate`: visible option, not selected
- `approved-direction`: selected style or route direction
- `binding-route`: controls final route composition
- `temporary-binding`: controls this milestone but needs later replacement
- `component-slot`: local, generated, sourced, or drawn asset that fills one mapped region
- `obsolete`: replaced or rejected

Do not use `component-slot` for a full route screenshot, full viewport mockup, or sliced screenshot that carries layout, readable text, navigation, or core controls.

## Resource Atomicity Gate

Before an asset slot record is accepted, create or cite a Resource-To-File Map from `resource-atomicity.md`.

The map must show whether each asset-controlled reference region is:

- an atomic resource unit
- a justified composite resource
- a coded CSS/DOM primitive
- an accepted gap

Split resources by edit, reuse, responsive, interaction, text, licensing, and replacement boundaries. Do not combine independent cards, icons, labels, controls, ornaments, product panels, textures, or diagram layers into one raster merely because they appear together in the reference.

If a single file carries multiple independently editable, reusable, interactive, localizable, sourced, or responsively positioned resources, classify it as `blocked-maintainability` until it is split or explicitly accepted for the milestone.

Composite assets are allowed only when the Resource-To-File Map records child pieces, why they can stay together, what must stay separate, text policy, edit boundary, and replacement trigger.

## Implementation Owner State

Each mapped reference region must have one owner:

- `dom-owner`: real layout, text, link, control, chart, form, table, or component
- `css-owner`: primitive shape, stroke, shadow, texture, layout decoration, or responsive crop
- `asset-owner`: local, generated, sourced, or drawn raster/vector asset in a defined component slot
- `accepted-gap`: explicitly not implemented for this milestone

No visible reference region can be `unowned`. If a region is not owned, broad implementation has not earned the right to start for that route.

## Asset Slot Record

Every generated, sourced, drawn, or local component-slot asset must record:

```md
| Route | Section | Reference Region | Resource Unit | Owner Component | Target Size/Aspect | Crop/Safe Padding | Must Match | Must Avoid | Text Policy | Perspective/Tilt Policy | Source Method | Output Path | Evidence Screenshot | Replacement Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Required fields:

- route
- section
- reference region
- owner component
- resource unit from the Resource-To-File Map
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

The output path should identify the atomic resource purpose, not a vague bucket such as `hero.png` when the file contains several independent resources.

## Text Policy

Use these values:

- `no-text`: asset must not contain readable text
- `ornamental-text-only`: visual marks are allowed but not readable content
- `real-dom-text-required`: all readable text must be DOM text
- `baked-text-approved`: readable text may be baked only when explicitly approved and not required for accessibility, SEO, localization, or interaction

Default to `real-dom-text-required` for UI, navigation, labels, cards, product panels, diagrams with labels, and content blocks.

If text must be baked into an image, record why it is acceptable and how accessibility, localization, and future editing will be handled.

## Perspective/Tilt Policy

Use these values:

- `css-applied`: image is front-facing; perspective, tilt, rotation, or shadow is applied in CSS
- `asset-baked`: perspective is part of the asset
- `mixed-with-reason`: both are used and the reason is recorded

Default to `css-applied` for reusable UI panels, cards, product frames, and diagrams. Use `asset-baked` only when the visual effect is intrinsic to the artwork or screenshot and cannot be reproduced safely in CSS.

## Difference-Driven Repair Loop

Each visual pass must record:

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

- Do not start another broad edit until the top 3 visible differences are named.
- The next edit must address at least one named difference.
- If a named difference is not fixed, move it to `accepted-gap` with a reason.
- New screenshots replace old proof. Old screenshots can remain as history, not final evidence.

## User Feedback State Machine

Treat user visual feedback as route evidence:

```text
not-matching -> blocked-visual
must-be-interactive -> blocked-p0-screenshot-guard
selected-this-direction -> approved-direction
use-this-as-reference -> binding-route or temporary-binding
this-is-deliverable -> close-enough
ship-it -> final review gate, not automatic Visual Delivery Ready
```

Positive feedback can narrow remaining work, but it must not erase required build, browser QA, text encoding, real DOM, or asset evidence.

## First-Viewport Composition Gate

For homepages and landing pages, record:

- binding reference viewport
- implementation viewport
- dominant visual system
- primary content block position
- next-section exposure
- whether lower sections compete with the hero
- whether decorative sections push primary content down
- status: `matched`, `accepted-gap`, or `blocked`

If the first viewport composition is blocked, the route cannot support `Visual Delivery Ready`.

## Mojibake And Text Encoding

Mojibake is both a content correctness failure and a visual delivery failure.

If visible UI text, final report text, or skill reference examples contain mojibake, the route or package cannot be considered delivery-ready.

Rules:

- Prefer ASCII-safe paraphrases in reusable skill docs when exact non-English examples are not required.
- Keep files UTF-8 when non-English examples are necessary.
- Treat unreadable generated text inside an asset as a failed text policy unless it is explicitly `ornamental-text-only`.

## Readiness Rules

The final route status cannot exceed the weakest asset slot or mapped region status.

`Visual Delivery Ready` requires:

- every visible binding-reference region has an implementation owner
- every asset-owned region has a Resource-To-File Map row
- every asset-owned region has an asset slot record
- every asset slot has text policy, perspective/tilt policy, output path, evidence screenshot, and status
- no asset slot remains `blocked-maintainability`
- top 3 visible differences from the latest pass are resolved or accepted
- first-viewport composition is `matched` or `accepted-gap`
- mojibake/text encoding status passes
- final report names visual asset pipeline status
