# Resource Atomicity

Use this reference when a binding route needs generated, sourced, drawn, extracted, or local visual assets.

The goal is maintainable webpage construction. Do not let visual proximity in a reference image decide file boundaries. Split resources by how they will be changed, reused, positioned, replaced, localized, licensed, and interacted with.

## Core Rule

Create separate resource files for separate semantic units unless a composite has an explicit reason.

An element should usually be its own file or coded primitive when it has independent:

- owner component
- reuse scope
- responsive position, crop, scale, or z-index
- hover, state, animation, or interaction behavior
- text, localization, accessibility, or SEO policy
- replacement trigger
- source, license, or attribution risk
- future edit reason
- visual role such as icon, ornament, texture, illustration, product panel, chart art, photo, mask, or shadow

Do not combine independent resources into one raster just because they sit near each other in the reference.

## Resource-To-File Map

Before generating, sourcing, drawing, extracting, or saving visual assets for a binding route, create a Resource-To-File Map:

```md
| Reference Region | Resource Unit | Unit Type | File Path | Owner Component | Reuse Scope | Split Reason | Must Stay Separate From | May Compose With | Text Policy | Edit Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hero board, top-right | blueprint panel background | product-panel | `public/assets/home/blueprint-panel.png` | `HeroBlueprintPanel` | route-specific | panel can tilt as one unit; labels remain DOM | nav, headline, CTA text | non-text diagram marks | no-text | replace panel art without changing layout links | planned |
```

Every asset-controlled visible region in a binding reference must be represented as:

- an atomic resource unit
- a justified composite resource
- a coded CSS/DOM primitive
- an accepted gap

No visible asset region may remain `visual memory only`.

## Unit Types

Use concrete unit types:

- `icon`
- `ornament`
- `texture`
- `illustration`
- `product-panel`
- `diagram-art`
- `photo`
- `background-plate`
- `mask`
- `shadow`
- `spritesheet`
- `css-primitive`
- `dom-component`
- `composite-with-reason`
- `accepted-gap`

Prefer specific types over generic names such as `hero.png` or `asset.png`. File names should describe the atomic resource purpose.

## Split Boundary Heuristics

Split resources when any answer is yes:

- Would this element be edited without editing its neighbor?
- Would it move, crop, hide, stack, or scale differently on mobile?
- Does it have independent hover, state, or animation behavior?
- Could it be reused on another card, page, or section?
- Does it have readable text, labels, numbers, or localization needs?
- Does it come from a different source or license?
- Could it be replaced by a future production asset while the surrounding layout remains?
- Would a designer naturally name it as its own layer in Figma?

Keep resources together only when the combined shape is one semantic illustration or panel and the child pieces are not expected to be independently edited, reused, translated, interacted with, or responsively positioned.

## Disallowed Mixed Assets

These block `Visual Delivery Ready` for binding routes:

- icon plus readable label baked into one image
- multiple cards or tiles baked into one image
- hero illustration plus navigation or header baked together
- product panel plus CTA, headline, or body copy baked together
- texture plus foreground object when either needs independent reuse or replacement
- chart or diagram art with readable labels that should be DOM text
- independent decorative props bundled into one file without a spritesheet contract
- full-route screenshots, full-viewport backgrounds, or sliced screenshots carrying layout, navigation, readable text, or controls

## Allowed Composites

Composite assets are allowed only when all are true:

- the asset represents one semantic illustration, product panel, texture plate, or diagram art unit
- readable text policy is satisfied
- child parts are not expected to move or respond independently
- source and replacement trigger are shared
- the Resource-To-File Map records why composition is safer than splitting
- the asset can fail to load without destroying route structure, navigation, readable text, or core interaction

For any composite, record:

- parent file path
- child visual pieces included
- why they can remain together
- what must stay outside the composite
- edit boundary
- replacement trigger

## Spritesheets

A spritesheet is a composite and needs a contract. Record:

- sprite file path
- included resources
- coordinates or named CSS variables/classes
- intended owner components
- why packed sprites are preferable to separate files
- text policy
- replacement trigger

Do not use spritesheets to hide unrelated page regions or avoid DOM/CSS composition.

## Prompt And Sourcing Rules

Before image generation, web sourcing, or drawing, write one asset prompt or sourcing record per atomic resource unit unless a composite is justified.

Each record must include:

- route and section
- reference region
- resource unit and unit type
- target component size or aspect ratio
- must-match details
- must-avoid details
- text policy
- transparent background or crop policy
- whether perspective, tilt, shadow, or rotation is baked into the image or applied in CSS
- output file path
- replacement trigger

If two resources need different prompt constraints, generate or source them separately.

## Runtime Composition Rule

Compose atomic resources in DOM/CSS when separate positioning, responsiveness, hover state, future editing, replacement, or reuse is expected.

Use code for:

- layout, cards, navigation, buttons, forms, labels, and readable text
- charts or diagrams whose values or labels need to remain editable
- repeated icons or ornament placement
- responsive layering and crop behavior

Use raster/vector files for:

- non-text artwork
- texture plates
- photos
- component-slot illustrations
- decorative or material details that are not practical as CSS primitives

## QA Gate

During visual QA, inspect every generated, sourced, drawn, extracted, or local asset used by a binding route.

Classify over-composition:

- `pass`: file contains one resource unit or justified composite
- `blocked-maintainability`: file contains multiple independently editable, reusable, interactive, localizable, sourced, or responsively positioned resources
- `blocked-visual`: file is a full-route screenshot, sliced route mockup, or layout-bearing raster shortcut
- `accepted-gap`: composition is known and allowed only for this milestone

If a single raster carries multiple independent resources, split it or justify the composite before claiming `Visual Delivery Ready`.

## Readiness Rules

`Visual Delivery Ready` requires:

- Resource-To-File Map exists for every binding route that uses visual assets
- every asset-owned visible region is mapped to an atomic unit, justified composite, CSS/DOM primitive, or accepted gap
- no resource file carries unrelated layout, navigation, readable text, controls, or multiple independent component units
- every generated/sourced/drawn asset has prompt or sourcing records tied to the resource unit
- QA records over-composition status
- final report states whether resource atomicity passed, is accepted-gap, or blocks delivery
