# zero-to-website-design V29 Resource Atomicity Plan

## Problem

The V28 visual asset pipeline records asset ownership and evidence, but it does not force agents to split visual resources by maintainable boundaries before generating, sourcing, drawing, or saving files.

In real website work this leaves a dangerous gap: multiple independent resources can be baked into one raster because they appear near each other in the reference image. That makes later edits brittle, prevents responsive repositioning, hides text or interaction boundaries, and turns a component system into a pile of composite images.

## Milestone

Add a resource atomicity contract to `zero-to-website-design` so visual assets are decomposed into maintainable file units before implementation.

## P0/P1 Scope

- Add a dedicated resource atomicity reference.
- Route the main skill, fidelity loop, visual asset pipeline, and implementation map through that reference.
- Add templates for Resource-To-File Maps and over-composition QA.
- Add regression coverage that protects the new contract.
- Validate the skill package and sync the local installed skill.

## Out Of Scope

- No automated image slicing tool.
- No rewrite of the full V20-V28 fidelity workflow.
- No changes to unrelated skills.
- No deletion of existing assets or docs.

## Resource Atomicity Rules

Assets must be split by future change reason, not by visual proximity.

An asset should stay separate when it has independent:

- reuse scope
- responsive position or crop
- hover, state, or interaction behavior
- text or localization policy
- replacement trigger
- source or licensing risk
- edit owner
- semantic role in the component tree

Composite assets are allowed only when they represent one semantic illustration or panel and their child pieces are not expected to move, change, translate, animate, or be reused independently.

## Required Artifact

Add a Resource-To-File Map:

```md
| Reference Region | Resource Unit | Unit Type | File Path | Owner Component | Reuse Scope | Split Reason | Must Stay Separate From | May Compose With | Text Policy | Edit Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

No generated/sourced/drawn/local asset can be accepted for a binding route unless it appears in this map or is explicitly marked as an accepted gap.

## QA Gate

Add an over-composition check:

- one raster carrying multiple independent cards, icons, labels, controls, decorations, or panels is `blocked-maintainability`
- a full route image, sliced route image, or screenshot-as-layout remains `blocked-visual`
- a spritesheet is allowed only when it declares coordinates, intended CSS use, and why sprite packing is better than separate files

## Expected Outcome

Future agents must first split resources into atomic units, write one prompt/source/draw action per resource unit unless a composite is justified, compose units through DOM/CSS, and record evidence that the runtime page remains maintainable.
