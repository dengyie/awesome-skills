# Zero-To-Website Design V2 Delivery Workflow

> Status: Draft for alignment
> Target package: `zero-to-website-design`
> Intent: turn the current generic v1 skill into a more complete website-delivery workflow based on the Little Lighthouse Folk Canvas project.

## Why V2

The current `zero-to-website-design` package is already valid and usable, but it still behaves more like a general orchestrator than a proven delivery playbook.

This V2 pass should capture what actually worked in production during the Folk Canvas rebuild:

1. Start from an explicit visual source, not from vague "make it pretty" instructions.
2. Write design docs before code.
3. Build framework and route skeletons before polishing content truth.
4. Reuse existing project images or historical mocks when image generation is constrained.
5. Use browser screenshots and production review as delivery gates, not optional polish.

## Primary Goal

Evolve `zero-to-website-design` into a skill that can guide a project from blank brief or loose references all the way to a practically deliverable website:

- project brief clarified
- visual authority documented
- design docs written
- route framework implemented
- local/mock assets integrated
- browser QA completed
- production review completed
- known gaps honestly reported

## What V2 Should Add

### 1. Historical Mock First Path

V1 covers two main paths well:

- no references -> generate concepts
- existing references -> implement from them

V2 should add a third first-class path:

- no new image generation for now -> reuse historical project images, old mockups, prior QA screenshots, or approved archives as temporary visual source material

This matters because real projects often hit one of these conditions:

- image generation is rate-limited or unavailable
- the user wants consistency with earlier concept work
- a previous design round already produced enough source images to start implementation
- the team wants framework-first delivery before commissioning final artwork

The skill should explicitly say:

- do not force `imagegen` when usable historical images already exist
- classify historical assets in the same provenance system as new assets
- allow "temporary binding" references for framework passes
- require a later asset-upgrade pass when temporary images stand in for final artwork

### 2. Delivery Phasing

V2 should make phased website delivery explicit.

Recommended phases:

1. Brief and visual-source phase
2. Design-doc phase
3. Framework implementation phase
4. Mock-asset integration phase
5. Route QA phase
6. Production hardening phase
7. Publish or handoff phase

This matches how the Folk Canvas project actually moved forward and prevents premature pixel-perfection work before the structure is stable.

### 3. Framework-First Acceptance

The skill should recognize a legitimate interim milestone:

`framework and format ready`

That means:

- layout shell exists
- header/footer/nav work
- route hierarchy is in place
- card systems and section rhythms exist
- typography scale is coherent
- placeholder or curated content is acceptable
- assets may still be mock or provisional

This milestone is especially useful when the user says things like:

- "build the site shell first"
- "focus on framework and format first"
- "content can wait"

### 4. Stronger Visual Provenance Levels

V1 already tracks provenance, but V2 should sharpen how image authority works in implementation.

Recommended authority levels:

- `exploratory`: only for style discovery
- `candidate`: waiting for user selection
- `approved-direction`: chosen for the design language, but not yet route-binding
- `binding-route`: implementation must match this route image
- `temporary-binding`: acceptable for current framework/mock pass, expected to be upgraded later
- `obsolete`: retained for history only

This prevents two common problems:

- concept images getting treated as final acceptance images
- temporary mock assets silently becoming permanent without review

### 5. Project Asset Strategy

V2 should tell the agent to choose among four asset modes in this order:

1. user-provided or repo-owned final assets
2. approved historical mock images
3. local CSS/SVG primitives that imitate the planned asset slots
4. generated images only when needed and allowed

This ordering better matches real delivery constraints than a generation-first workflow.

## Proposed Changes To The Skill Package

### Keep

- `SKILL.md`
- current `references/`
- current `assets/templates/`
- current tests and usage docs

### Add

- `references/historical-mock-pass.md`
- `assets/templates/mock-asset-pass.md`
- one usage section documenting the "no imagegen / reuse historical images" path

### Update

- `SKILL.md`
- `references/concept-generation.md`
- `references/visual-provenance.md`
- `references/implementation-map.md`
- `references/route-acceptance.md`
- `references/production-delivery.md`
- `docs/usage/zero-to-website-design.md`
- tests so the new reference/template files are required

## Proposed SKILL.md Direction

The main `SKILL.md` should stay concise, but V2 should revise the workflow wording like this:

1. Restore project context.
2. Run intake.
3. Collect visual sources.
4. Classify provenance and authority.
5. Choose the right source path:
   - generate concepts
   - implement from user references
   - implement from historical mock assets
6. Write design docs before code.
7. Produce an implementation map.
8. Build framework before detail polish.
9. Integrate mock/final assets.
10. Verify with build and browser QA.
11. Run production review.
12. Deliver with known gaps and next-pass notes.

The critical improvement is that the skill should no longer imply that image generation is the natural next step whenever references are weak.

## New Reference: `historical-mock-pass.md`

This reference should explain how to do a mock-asset pass when no new images will be generated yet.

Suggested contents:

### When to read it

Read when:

- the user says not to generate new images yet
- the repo already contains design concepts, prior exports, old screenshots, or archived art
- the current goal is framework-first delivery

### What counts as a historical mock asset

- approved concept PNGs
- screenshots from earlier implementation rounds
- exported page captures
- prior brand or illustration studies
- old project-owned visual assets not yet fully productized

### Workflow

1. Inventory existing visual files.
2. Mark each one with provenance and authority.
3. Decide whether it can drive:
   - whole route layout
   - section composition
   - illustration slot shape only
   - palette/texture only
4. Record limitations.
5. Use them as local mock assets or design references.
6. Write an asset-upgrade note for later replacement if needed.

### Guardrails

- do not present provisional historical imagery as final bespoke artwork
- do not mix obsolete and binding references
- do not hotlink when a local project-owned file exists
- do not skip QA just because the asset is temporary

## New Template: `mock-asset-pass.md`

This template should be a compact project doc with sections like:

- Goal
- Routes in scope
- Historical assets used
- Temporary binding assets
- Asset slot mapping
- Known visual limitations
- Upgrade triggers
- QA checklist

This gives the agent a lightweight document for the exact situation the Folk Canvas project is in now.

## Route Acceptance Changes

V2 should extend route acceptance to distinguish two success levels:

### Level A: Framework Ready

- route shell matches the planned composition
- responsive layout is stable
- nav, cards, and content regions behave correctly
- no overflow, clipping, or dead interactions
- placeholder/mock assets are correctly placed

### Level B: Visual Delivery Ready

- route has the intended final or approved-temporary visual assets
- spacing, hierarchy, and emphasis are close to the binding source
- known visual differences are minor and explicitly listed

This split will make the skill much more usable in real project sequencing.

## Production Delivery Changes

Production delivery guidance should explicitly require:

- a check that temporary-binding assets are acknowledged in the final report
- a check that content truth vs framework placeholder status is stated
- a check that source-of-truth data and exported routes match
- a check that no placeholder brand survives in active UI

This reflects the real issues caught during the Little Lighthouse delivery passes.

## Testing And Validation Plan

After the V2 edits:

1. Run skill validation.
2. Run package tests.
3. Add or update regression tests for:
   - new reference and template presence
   - presence of temporary-binding provenance language
   - presence of historical-mock workflow language
   - presence of framework-ready vs delivery-ready route gates
4. Run `production-code-quality-review` on `awesome-skills`.

## Acceptance Criteria For This V2 Doc

This development direction is aligned if we agree on these points:

- `zero-to-website-design` stays general-purpose, not Little Lighthouse-specific
- `imagegen` remains optional, not mandatory
- historical repo images become a first-class input path
- framework-first delivery is treated as a valid milestone
- visual provenance gains a temporary-binding concept
- route acceptance is split into framework-ready and delivery-ready

## Recommended Next Implementation Step

If this direction looks right, the next concrete pass should be:

1. update the dev plan/checklist
2. add `historical-mock-pass.md`
3. add `mock-asset-pass.md`
4. revise `SKILL.md` and the affected references
5. update tests and usage docs
6. run validation and review
