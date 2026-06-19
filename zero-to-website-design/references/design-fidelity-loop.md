# Design Fidelity Loop

Use this reference whenever a user provides a design screenshot, mockup, Figma export, generated route mockup, or any other image that should control the final page.

The goal is not blind pixel perfection. The goal is to make visual differences explicit, fix the ones that block the current milestone, and avoid shipping a page that only vaguely resembles the design.

## Entry Conditions

Run a fidelity pass when any of these is true:

- a reference image is classified as `binding-route` or `temporary-binding`
- the user says the implementation is too far from the design
- the milestone target is `Visual Delivery Ready`
- a generated route mockup or historical mockup controls route layout, mood, or component shape

Do not claim visual parity from memory. Use screenshots.

## Reference-Image Failure Mode

Do not treat a reference image as a palette, mood board, or vague style hint when it has route authority.

Palette-only restyling is a blocking failure: if the implementation just recolored the page, changed border radius, swapped fonts, or copied a few accents while the layout geometry, component silhouette, decorative resources, hierarchy, density, and responsive composition still differ from the reference, the route is still `blocked`.

This reference-image failure mode must trigger a rework pass:

- reclassify the design image as a binding component and layout contract
- redraw or code the missing component silhouettes
- draw or generate the missing UI assets, ornaments, illustrations, panels, textures, icons, or decorative resources
- replace generic cards/sections with shapes that match the reference
- capture a new implementation screenshot and compare it side-by-side before claiming improvement

Do not downgrade this to polish. It is a P1 visual correctness issue when the milestone says to match the design.

## Reference Decomposition

Before broad implementation, decompose every binding reference into implementable facts:

- canvas size and viewport
- page background, section backgrounds, and visible color tokens
- grid, max width, columns, gutters, margins, and section heights
- typography families or closest available substitutes, font sizes, weights, line heights, and casing
- component inventory and repeated patterns
- image, icon, ornament, texture, and illustration slots
- border radius, shadows, strokes, dividers, blur, and depth rules
- navigation and interaction states visible or implied
- mobile or responsive differences when the reference includes them
- component silhouette and custom resource inventory, including any shapes or assets that must be drawn, coded, or generated

Record unknowns instead of guessing silently. If a visual fact cannot be derived from the image, mark it as an assumption and validate it through the screenshot loop.

## Fidelity Budget

For each route, define what must match for the current milestone:

- `blocking`: route composition, hero proportions, major colors, typography scale, spacing rhythm, key assets, visible state, and responsive ordering that materially define the design
- `accepted-gap`: differences the user or milestone permits, such as final copy, production photography, low-risk microcopy, or intentionally deferred animation
- `out-of-scope`: routes, states, or breakpoints not used to support the readiness claim

`Framework Ready` can allow more accepted visual gaps, but it still requires route composition and responsive structure to match the binding reference.

`Visual Delivery Ready` requires blocking visual deviations to be fixed or explicitly downgraded with rationale.

## UI Asset And Component Prompting

Use image generation when a design needs bespoke UI imagery that the repo does not already have and CSS/HTML alone cannot reproduce convincingly.

Good candidates:

- hero illustrations
- product screenshots or abstract app panels
- texture plates
- icon families
- decorative motifs
- card artwork
- background images
- route-specific empty-state art

Prefer coded HTML/CSS components for real controls, readable text, layout, navigation, and repeated UI primitives. Generate images for visual assets, not for core interaction logic.

If a design reference depends on a distinctive component silhouette or illustration resource, make the resource explicitly instead of approximating it with a generic rectangle.

### Prompt Template

Write asset prompt records before generation:

```text
Asset prompt:
- Route/section:
- Source reference path:
- Purpose:
- Must match:
- Must avoid:
- Aspect ratio / pixel target:
- Transparent background needed:
- Style keywords:
- Text policy:
- Output filename:
- Replacement trigger:
```

Prompt for concrete website UI assets, not vague mood art. Name the visual role, palette, shape language, composition, and crop. If the asset must fit a component slot, include exact aspect ratio and safe padding.

If generation output is used, record it in the visual source map with source method `imagegen`, authority status, ownership scope, milestone supported, and replacement trigger.

## Implementation Screenshot Loop

During development, capture an implementation screenshot at the same viewport as the reference.

For each binding route/viewport, record:

- reference screenshot path
- implementation screenshot path
- side-by-side comparison path or QA note path
- viewport dimensions
- difference summary
- blocking visual deviations
- accepted visual gaps
- next fix action
- fidelity status: `not-checked`, `blocked`, `close-enough`, or `matched`

Use Side-by-side comparison even if there is no automated image diff. A simple image pair, browser screenshot beside the source, or documented comparison table is enough when it identifies concrete deviations.

## Fix Loop

Fix in this order:

1. route composition and section order
2. canvas width, max width, grid, and gutters
3. vertical spacing and section heights
4. typography scale and line-height
5. color, contrast, and background treatment
6. image and illustration placement
7. component radius, shadows, borders, and density
8. responsive/mobile ordering and crop behavior
9. micro-interactions and polish

After each meaningful fix, recapture the screenshot for the affected viewport. Do not keep editing from memory after the page has drifted from the reference.

## Final Acceptance

Before claiming `Visual Delivery Ready`, the final QA evidence must show:

- every binding route has reference and implementation screenshots
- each required viewport has a side-by-side comparison or equivalent comparison note
- blocking visual deviations are fixed
- remaining gaps are accepted and named
- generated UI assets are recorded with prompt, path, authority, and replacement trigger
- final readiness follows the weakest route fidelity status

Do not claim visual parity, pixel match, or design fidelity if the final evidence only checked layout health, build status, or generic screenshot QA.
