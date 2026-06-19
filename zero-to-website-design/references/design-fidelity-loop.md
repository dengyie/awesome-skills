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

## Interactive Implementation Requirement

Do not ship a binding reference as a full-page screenshot.

A selected design image is a construction contract for an interactive webpage, not the webpage itself. The implementation must rebuild the page as real DOM, components, text, controls, charts, links, and responsive behavior. Use the reference screenshot for analysis and QA evidence, not as the primary rendered surface.

Screenshot-as-page implementation is a blocking failure when a route uses the whole reference image as an `<img>`, page background, canvas bitmap, or similar full-viewport raster layer and then adds transparent hotspots, invisible links, or minimal overlay text to simulate interactivity.

This anti-pattern fails even if the first viewport looks visually identical because it breaks accessibility, responsive adaptation, content maintainability, SEO, real interactions, state changes, and design-system evolution.

Allowed uses of screenshots:

- reference screenshot may be used for QA evidence, side-by-side comparison, annotation, or crop analysis
- local raster assets may be created from the reference only for limited non-interactive artwork such as textures, illustrations, ornaments, or product-image slots
- generated or sourced imagery may support a component slot when text, links, controls, layout, and state remain implemented as page structure

When a design includes complex charts, diagrams, product panels, or custom artwork, build or source the necessary resources intentionally:

- code charts, tables, controls, navigation, forms, cards, and text-heavy panels as real components
- draw or generate illustrations, textures, and decorative resources as local assets
- use web-sourced assets only when needed, record source and replacement risk, and localize them when licensing and project policy allow
- keep transparent clickable overlays only as temporary annotation/debug aids, never as the shipped interaction model

If the current implementation relies on a full-page screenshot, classify the route as `blocked`, replace the screenshot surface with real structure, and recapture screenshots before requesting signoff.

## Reference Decomposition

Before broad implementation, decompose every binding reference into implementable facts:

- canvas size and viewport
- page background, section backgrounds, and visible color tokens
- grid, max width, columns, gutters, margins, and section heights
- typography families or closest available substitutes, font sizes, weights, line heights, and casing
- component inventory and repeated patterns
- interactive element inventory, including buttons, links, forms, tabs, menus, charts, diagrams, and stateful regions that must be implemented rather than flattened into an image
- image, icon, ornament, texture, and illustration slots
- border radius, shadows, strokes, dividers, blur, and depth rules
- navigation and interaction states visible or implied
- mobile or responsive differences when the reference includes them
- component silhouette and custom resource inventory, including any shapes or assets that must be drawn, coded, or generated

Record unknowns instead of guessing silently. If a visual fact cannot be derived from the image, mark it as an assumption and validate it through the screenshot loop.

## Reference-To-DOM Map

Before implementation, create a Reference-To-DOM Map for every binding route. This is the bridge from image analysis to real webpage construction.

Use this table shape in the implementation plan or equivalent artifact:

```md
| Reference Region | DOM Component | Text Real DOM? | Asset Strategy | Interaction | Must Not Do |
| --- | --- | --- | --- | --- | --- |
| Hero right blueprint panel | `HeroBlueprintPanel` | yes for labels and buttons | generated component-slot asset for non-text illustration; CSS applies tilt | real links and hover state | do not paste full hero screenshot or bake readable text into the image |
```

Each visible region in the binding screenshot must be classified as one of:

- real DOM/layout
- CSS-drawn primitive
- generated/local component-slot asset
- accepted gap

No region may remain `visual memory only`. If a region is visible in the reference but has no mapped component, asset strategy, or accepted-gap rationale, broad implementation has not earned the right to start.

## Component-Slot Raster Asset Rules

Screenshots are not deliverables, but component-slot raster assets are allowed when they support a real webpage structure.

Allowed component-slot raster assets:

- decorative props
- material textures
- illustrations inside cards
- product or diagram panels
- non-text ornamental notes
- bespoke art that sits inside a component with real surrounding layout and controls

Disallowed runtime raster shortcuts:

- full-route screenshots
- full-viewport background mockups
- sliced screenshots that carry layout, readable text, navigation, or core controls
- transparent hotspots over static images
- generated page images that replace DOM hierarchy

When in doubt, ask whether the page would still have meaningful structure, readable text, links, state, and responsive behavior if the asset failed to load. If not, the asset is carrying too much of the route.

## Page Item Fidelity Audit

For every binding route and required viewport, create an itemized comparison table before claiming visual readiness.

Do not replace this with a paragraph summary. The audit must make the agent compare the design image and implementation one page item at a time.

Required item categories:

- route canvas, viewport, background, and page bounds
- header, navigation, logo, and primary actions
- hero composition, headline block, supporting copy, calls to action, and hero assets
- every visible section in order, including section height, grid, gutters, and alignment
- repeated components such as cards, lists, chips, tabs, forms, stats, timelines, and galleries
- typography blocks, font scale, line-height, weight, casing, and text density
- color treatments, strokes, shadows, borders, radius, blur, and depth
- illustrations, product shots, icons, ornaments, textures, dividers, and decorative resources
- spacing relationships between neighboring components and sections
- responsive/mobile ordering, cropping, stacking, and hidden or revealed elements

Use this table shape in the project QA report or equivalent artifact:

```md
| Route | Viewport | Design Item | Reference Region | Implementation Region | Evidence Quality | Match Status | Deviation | Severity | Fix Action | Recheck Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/` | 1440x900 | Hero illustration silhouette and position | reference-home.png region: top-right hero panel, or crop ref-home-hero.png | qa-home-1440.png region: hero right column, or crop qa-home-hero.png | specific | blocked | Missing custom illustration silhouette and crop | blocking | Draw or generate matching hero panel and recapture screenshot | pending |
```

Allowed item match statuses:

- `matched`: implementation matches the reference closely enough for the current milestone
- `accepted-gap`: deviation is named, allowed by the fidelity budget, and not used to overclaim readiness
- `blocked`: deviation materially changes the design's layout, hierarchy, component silhouette, custom asset, or responsive behavior
- `not-checked`: item has not been compared with evidence

Failure rules:

- Any `not-checked` required item blocks `Visual Delivery Ready`.
- Any `blocked` item blocks `Visual Delivery Ready`.
- A route with only a high-level screenshot comparison but no itemized audit blocks `Visual Delivery Ready`.
- Audit rows with vague evidence such as "looks close", "same section", or "see screenshot" but no route, viewport, reference region, and implementation region count as `not-checked`.
- A route implemented as a full-page reference screenshot with transparent hotspots remains `blocked` until the page is rebuilt as interactive DOM/components/assets.
- A route with generic components where the reference shows distinctive silhouettes, assets, or ornaments remains `blocked` until those items are drawn, coded, generated, or explicitly accepted as gaps.
- The final readiness claim must follow the weakest required item status across every binding route and viewport.

## Verifiable Evidence Rules

Each itemized audit row must be checkable by another agent without trusting the original author's judgment.

For every required design item, record:

- reference screenshot path
- implementation screenshot path
- viewport
- reference region, crop path, coordinate range, or clearly named visual area
- implementation region, crop path, coordinate range, or clearly named visual area
- evidence quality: `specific`, `annotated`, `cropped`, or `weak`
- match status
- deviation and severity
- fix action for `blocked` or `weak` rows
- recheck evidence after any fix

Evidence quality rules:

- `specific`: row points to concrete screenshot paths and named regions that another reviewer can locate.
- `annotated`: row points to an image or note with marked regions.
- `cropped`: row points to reference and implementation crops for the item.
- `weak`: row is too vague to verify independently.

Rows marked `weak` cannot support `Visual Delivery Ready`. If a row is fixed, update its implementation screenshot or crop and set `Recheck Evidence`; do not leave the old evidence as proof of the final state.

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

Read `visual-asset-pipeline.md` when generated, sourced, drawn, or local visual assets need ownership, text policy, perspective/tilt policy, evidence screenshots, and delivery-status tracking.

### Prompt Template

Write asset prompt records before generation:

```text
Asset prompt:
- Route/section:
- Source reference path:
- Target component size/aspect ratio:
- Reference region:
- Purpose:
- Must match:
- Must avoid:
- Aspect ratio / pixel target:
- Transparent background needed:
- Style keywords:
- Text policy:
- Perspective/tilt ownership: baked into image or applied in CSS
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
- top 3 visible differences before the next edit pass
- blocking visual deviations
- accepted visual gaps
- next fix action
- fidelity status: `not-checked`, `blocked`, `close-enough`, or `matched`
- link or path to the itemized fidelity audit for that route and viewport

Use Side-by-side comparison even if there is no automated image diff. A simple image pair, browser screenshot beside the source, or documented comparison table is enough when it identifies concrete deviations.

After every visual pass, name the top 3 visible differences before editing again. Do not continue polishing from memory. The next edit pass must respond to the named differences or explicitly move them to accepted gaps.

## User Feedback Status Updates

Treat user visual feedback as route evidence, not as casual commentary.

- "not matching", "far from the reference", or equivalent feedback sets the route to `blocked-visual`.
- "not a screenshot", "must be interactive", or equivalent feedback makes the screenshot-as-page guard a P0 blocker.
- "this is deliverable", "close enough to review", or equivalent feedback may set the current pass to `close-enough`, after which further work should be scoped polish, not a new broad redesign.

Do not report completion while the latest named user mismatch remains unresolved or unaccepted.

## Visual Usability Gate

A visually driven page is not ready merely because lint, build, export, or route smoke tests pass.

Check:

- brand, product, person, object, or site purpose is immediately recognizable
- primary hierarchy matches the binding reference
- key custom assets are present, not generic placeholders
- text is readable and not mojibake
- first-viewport composition follows the reference, including whether the next section is only hinted
- lower sections do not compete with the hero unless the reference does so
- primary content is not pushed down by decorative sections
- the page would not be embarrassing to show as a first review build

Any failure here is a `blocking-visual` issue for `Visual Delivery Ready`.

## Fix Loop

Fix route-level and item-level mismatches in this order:

1. route composition and section order
2. canvas width, max width, grid, and gutters
3. vertical spacing and section heights
4. typography scale and line-height
5. color, contrast, and background treatment
6. image and illustration placement
7. component radius, shadows, borders, and density
8. responsive/mobile ordering and crop behavior
9. micro-interactions and polish

After each meaningful fix, recapture the screenshot for the affected viewport and update the affected audit rows. Do not keep editing from memory after the page has drifted from the reference.

## Final Acceptance

Before claiming `Visual Delivery Ready`, the final QA evidence must show:

- every binding route has reference and implementation screenshots
- each required viewport has a side-by-side comparison or equivalent comparison note
- top 3 visible differences have been named after the latest visual pass and resolved or accepted
- a Reference-To-DOM Map exists for every binding route
- each binding route and required viewport has an itemized fidelity audit covering the required page items
- no required page item remains `not-checked` or `blocked`
- no required page item has `weak` evidence quality
- every fixed item has fresh recheck evidence after the fix
- blocking visual deviations are fixed
- remaining gaps are accepted and named
- generated UI assets are recorded with prompt, path, authority, and replacement trigger
- component-slot asset records explain size/aspect ratio, reference region, text policy, and perspective/tilt ownership
- visual usability gate passes, including no mojibake and correct first-viewport composition
- final readiness follows the weakest route fidelity status

Do not claim visual parity, pixel match, or design fidelity if the final evidence only checked layout health, build status, or generic screenshot QA.
