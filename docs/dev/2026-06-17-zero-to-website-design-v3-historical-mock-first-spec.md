# Zero-To-Website Design V3 Historical-Mock-First Spec

> Status: Draft for alignment
> Target package: `zero-to-website-design`
> Intent: turn the current website-design skill into a stronger delivery playbook based on the Little Lighthouse implementation workflow that actually shipped usable results.

## Summary

The current `zero-to-website-design` package is already directionally right, but it still reads more like a good general orchestrator than a battle-tested website delivery workflow.

This V3 pass should make one thing explicit:

`build from the best available visual authority first, not from a mandatory image-generation step`

That means the skill should support four practical source paths in this order:

1. repo-owned final assets or user-provided approved references
2. approved historical mockups or prior project design images
3. local CSS/SVG structural mock assets
4. newly generated images, only when needed and allowed

This ordering matches what worked in the Little Lighthouse project and better reflects real delivery constraints.

## Why V3 Is Needed

The current package already covers:

- blank brief -> generate concepts -> implement
- existing references -> map and implement

What it still does not treat strongly enough is the most common real-world middle state:

- the team already has historical images, concept exports, or prior screenshots
- the user wants the site framework built now
- image generation is unavailable, undesirable, rate-limited, or simply unnecessary

In that state, the skill should not behave as if fresh concept generation is the natural next move.

## Design Goal

Evolve `zero-to-website-design` into a skill that can take a project from loose idea or partial references to a practically deliverable website by following this sequence:

1. clarify the brief
2. inventory all available visual sources
3. classify visual authority and provenance
4. write design docs before code
5. build framework and route skeletons first
6. use historical or local mock assets when final art is not ready
7. verify with browser QA
8. run production review
9. report known gaps honestly

## Core Product Principles

### 1. Historical Mock First Is A First-Class Path

The skill must explicitly support:

- approved concept PNGs already in the repo
- screenshots from prior implementation rounds
- old exported-page captures
- archived visual studies
- existing project-owned illustrations or photos

These should be treated as valid inputs, not second-class fallbacks.

The skill should say:

- do not force `imagegen` when historical visual sources are already sufficient
- classify historical assets in the same provenance system as generated or uploaded assets
- allow `temporary-binding` assets for framework-first passes
- require later upgrade notes when temporary assets stand in for final artwork

### 2. Design Docs Before Code

The skill should keep the existing rule and make it sharper:

- no coding before a compact design contract exists
- no visual implementation before route ownership is clear
- no route implementation before a source map identifies which image controls that route

Minimum docs for a real project:

- `design-system/MASTER.md`
- `design-system/IMPLEMENTATION-PLAN.md`
- `design-system/ASSET-AND-DATA-SPEC.md`
- `design-system/pages/<route>.md`
- `design-system/VISUAL-SOURCE-MAP.md`

### 3. Framework-First Delivery Is A Valid Milestone

The skill should recognize a meaningful intermediate state:

`framework ready`

That means:

- route structure exists
- header, nav, footer, and page shell work
- major layout regions match the intended composition
- card/list/detail systems exist
- typography hierarchy is coherent
- placeholder or curated content is acceptable
- provisional historical/local mock assets are acceptable

This is different from:

`visual delivery ready`

That second state requires closer fidelity, stronger assets, cleaner metadata, and final QA confidence.

### 4. Visual Provenance Must Carry More Authority States

The current provenance model is close, but V3 should use clearer authority levels:

- `exploratory`
- `candidate`
- `approved-direction`
- `binding-route`
- `temporary-binding`
- `obsolete`

This solves two common failure modes:

1. a moodboard or concept image accidentally becoming the acceptance target
2. a temporary framework mock silently becoming permanent without review

### 5. Production Review Is Part Of Design Delivery

The website-design workflow should explicitly treat production review as part of the job, not an optional add-on.

Before calling a website pass complete, the skill should require:

- build or typecheck verification
- browser QA on desktop and mobile
- route/data/metadata consistency checks
- placeholder brand scan
- production-oriented code review

## Proven Workflow To Encode

This is the workflow that actually worked in the Little Lighthouse project and should become the V3 baseline:

1. Restore project context and constraints.
2. Read design-system docs or create them if missing.
3. Inventory available images in the repo before considering generation.
4. Mark each image with provenance and authority.
5. Decide whether each image controls:
   - route composition
   - section composition
   - illustration slot shape
   - palette and texture only
6. Write or update route specs.
7. Produce an implementation map before code.
8. Build the framework and format first.
9. Use local or historical assets to fill the intended visual slots.
10. Run build and browser QA.
11. Run production review.
12. Publish or hand off with known visual and content gaps listed.

## Recommended Skill Workflow Revision

The next `SKILL.md` iteration should move to this order:

1. Restore project context.
2. Run intake.
3. Collect visual sources.
4. Classify provenance and authority.
5. Choose the correct source path:
   - user or repo-owned final references
   - historical mock assets
   - local structural mock assets
   - new concept generation
6. Write design docs before code.
7. Produce an implementation map.
8. Build framework before detail polish.
9. Integrate mock or final assets.
10. Verify with build and browser QA.
11. Run production review.
12. Deliver with known gaps and next-pass notes.

## Package Changes Proposed For V3

### Keep

- `zero-to-website-design/SKILL.md`
- existing `references/`
- existing `assets/templates/`
- existing tests
- existing usage docs

### Add

- `references/historical-mock-pass.md`
- `references/framework-first-delivery.md`
- `assets/templates/mock-asset-pass.md`
- `assets/templates/visual-source-inventory.md`

### Update

- `SKILL.md`
- `references/concept-generation.md`
- `references/visual-provenance.md`
- `references/design-system-docs.md`
- `references/implementation-map.md`
- `references/route-acceptance.md`
- `references/visual-qa-checklist.md`
- `references/production-delivery.md`
- `docs/usage/zero-to-website-design.md`
- `README.md`
- package tests

## New Reference: `historical-mock-pass.md`

This should explain how to proceed when new image generation is not the right move.

### When To Read It

Read when:

- the user says not to generate new images yet
- the repo already contains concept PNGs, screenshots, or archived visual assets
- the project goal is framework-first delivery
- existing project visuals are strong enough to guide composition

### What Counts As Historical Mock Material

- approved concept boards
- route mockups from earlier phases
- exported screenshots from prior builds
- old design explorations that still match the chosen direction
- project-owned art or textures not yet fully integrated

### Required Output

The reference should require a compact note that records:

- historical assets found
- their authority status
- what route or section each one controls
- whether they are `temporary-binding`
- what must later be upgraded

## New Reference: `framework-first-delivery.md`

This should make phased implementation explicit.

Recommended delivery phases:

1. brief and visual-source phase
2. design-doc phase
3. framework implementation phase
4. mock-asset integration phase
5. route QA phase
6. production hardening phase
7. publish or handoff phase

It should also define two route states:

- `Framework Ready`
- `Visual Delivery Ready`

## Template Changes

### New Template: `mock-asset-pass.md`

Purpose: give projects a lightweight doc for the framework-first stage.

Suggested sections:

- Goal
- Routes in scope
- Historical assets used
- Temporary-binding assets
- Asset-slot mapping
- Known limitations
- Upgrade triggers
- QA evidence

### New Template: `visual-source-inventory.md`

Purpose: make visual provenance faster to record at project start.

Suggested fields:

- Asset path
- Source method
- Status
- Route or section ownership
- Viewport
- Notes

## Required Reference Revisions

### `references/concept-generation.md`

Revise so it no longer implies concept generation is the default answer.

It should explicitly say:

- first inspect repo-owned or user-provided visuals
- use historical mock assets when sufficient
- use generation only when the project lacks enough authority to proceed

### `references/visual-provenance.md`

Revise status values and examples to include:

- `approved-direction`
- `binding-route`
- `temporary-binding`

Also add `existing-project-mockup` as a first-class source method.

### `references/implementation-map.md`

Revise to require:

- asset strategy selection
- framework-first milestone definition
- explicit desktop/mobile source ownership
- known visual risk list

### `references/route-acceptance.md`

Split route acceptance into two levels:

#### Level A: Framework Ready

- shell and layout regions are in place
- navigation works
- responsive behavior is stable
- cards, detail surfaces, and section bands exist
- placeholder or temporary-binding assets are correctly placed
- no overflow, dead links, or broken interaction states

#### Level B: Visual Delivery Ready

- route matches the binding reference closely
- asset quality is acceptable for delivery
- spacing and hierarchy are tuned
- metadata and content framing are coherent
- known remaining differences are minor and documented

### `references/production-delivery.md`

Add explicit checks for:

- temporary-binding assets acknowledged in final report
- framework-first versus final-content status stated clearly
- no placeholder brand in active UI
- route/data/SEO/export consistency
- production review completed

## Testing Plan For The V3 Implementation Pass

After the actual package edits land:

1. run skill validation
2. run package unit tests
3. add regression tests for:
   - new reference files exist
   - new template files exist
   - provenance statuses include temporary-binding flow
   - usage docs include historical-mock workflow
   - route acceptance distinguishes framework-ready and delivery-ready
4. run `production-code-quality-review`
5. fix confirmed findings before release

## Acceptance Criteria For This V3 Direction

We should consider this spec aligned if we agree on these points:

- `zero-to-website-design` remains a general website skill, not a project-specific skill
- historical repo images are a first-class input path
- `imagegen` stays optional
- design docs remain mandatory before code
- framework-first delivery is treated as a valid milestone
- provenance gains a `temporary-binding` concept
- QA plus production review remain required before final delivery

## Recommended Next Step

If this direction looks right, the next implementation pass should be:

1. update the development checklist
2. add the two new references
3. add the two new templates
4. revise `SKILL.md` and affected references
5. update usage docs and tests
6. run validation and production review
7. release the updated skill package
