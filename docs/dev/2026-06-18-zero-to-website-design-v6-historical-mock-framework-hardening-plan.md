# Zero-To-Website Design V6 Historical-Mock Framework Hardening Plan

> Status: Draft for alignment
> Target package: `zero-to-website-design`
> Phase type: workflow and template hardening

## Goal

Encode the strongest practical lesson from the Little Lighthouse delivery work into the general website-design skill:

`when a repo already has usable mockups, screenshots, or prior concept images, use them to drive a framework-ready website pass before reaching for fresh image generation`

This phase should turn that lesson from implied guidance into a clearer, more operational workflow for real projects that start in the messy middle:

- the user wants the site built now
- final imagery is not ready
- the repo already contains useful visual material
- the first milestone is framework and format, not final bespoke art

## Why This Phase

The shipped package already has the right foundations:

- V3 made historical mock inputs first-class
- V4 added Level 3 project-memory behavior
- V5 made the templates memory-aware

What is still under-specified is the actual delivery behavior when the user says some version of:

- use the images already in the project
- do not generate new images yet
- build the site skeleton and route framing first
- content and art can wait; get the framework deliverable

That path was central to the Little Lighthouse implementation, but the current package still leaves too much of the execution detail implicit.

## Product Intention

This phase should make `zero-to-website-design` better at one concrete kind of work:

1. inventory project-owned visual files
2. decide which ones can temporarily own route composition
3. document those choices before code
4. build the website shell, route structure, layout rhythm, and component framing first
5. use historical assets only as local mock drivers, not as falsely-final art
6. report clearly what is framework-ready and what still needs final asset upgrades

## Scope

In scope:

- add a new development note describing the historical-mock framework-first delivery pass
- tighten wording in package docs and references so this path is easier to follow
- make the mock-asset documentation more explicit about route ownership and upgrade criteria
- strengthen usage examples around "do not generate images yet"
- extend tests if the shipped skill text/template wording changes
- update project memory for the new stage

Out of scope:

- building a project-specific Folk Canvas skill into this package
- requiring image generation for every website workflow
- adding heavy automation that extracts layouts from screenshots
- removing the existing concept-generation path

## Little Lighthouse Pattern To Generalize

The real workflow that proved useful looked like this:

1. collect repo-owned screenshots, concept PNGs, and earlier route mockups
2. classify which images control full routes versus only sections or asset slots
3. create design docs before code so the image authority is explicit
4. ship route shells, nav, footer, cards, spacing rhythm, and responsive behavior first
5. keep content curated or placeholder when framework delivery is the milestone
6. use local CSS/SVG or reused historical imagery to fill asset slots
7. verify with build plus desktop/mobile browser QA
8. report visual gaps honestly instead of pretending the temporary imagery is final

That should become a named, obvious path in the package.

## Workflow Additions Proposed For V6

### 1. Add an explicit "historical mock framework pass"

The skill should recognize a sub-path where:

- historical or repo-owned visuals are sufficient to bind route structure
- the user explicitly defers final generated art
- the current milestone is `Framework Ready`

This path should tell the agent to:

- prefer local project images first
- generate only if the current framework pass lacks enough visual authority to continue
- keep temporary visual ownership visible in docs and handoff notes

### 2. Sharpen temporary-binding rules

`temporary-binding` is already part of the package, but this phase should make its practical meaning clearer.

For framework-first website work, every temporary-binding image should answer:

- what route or section it controls
- whether it controls composition, asset-slot shape, or only palette/texture
- what would trigger its replacement
- whether the route can still be called framework-ready with it in place

### 3. Distinguish framework composition from asset finality

The package should make it easier to say:

- route composition is accepted
- responsive structure is accepted
- interactive surfaces are accepted
- current imagery is still provisional

That split is what makes the workflow useful in real delivery, and it should appear consistently in docs, templates, QA notes, and final reports.

### 4. Make "no new images yet" a first-class usage path

The usage docs should give a direct example like:

```text
Use $zero-to-website-design to rebuild this site from the historical PNG mockups already in the repo. Do not generate new images yet; first get the framework and route layout to a deliverable state.
```

## Files Likely To Change In The Implementation Phase

If this plan is accepted, the next implementation pass will likely touch:

- `zero-to-website-design/SKILL.md`
- `zero-to-website-design/references/historical-mock-pass.md`
- `zero-to-website-design/references/framework-first-delivery.md`
- `zero-to-website-design/references/implementation-map.md`
- `zero-to-website-design/references/route-acceptance.md`
- `zero-to-website-design/references/production-delivery.md`
- `zero-to-website-design/assets/templates/mock-asset-pass.md`
- `zero-to-website-design/assets/templates/visual-source-inventory.md`
- `docs/usage/zero-to-website-design.md`
- `zero-to-website-design/tests/test_skill_package.py`

## Documentation Changes Proposed

### `historical-mock-pass.md`

Add clearer guidance for:

- route-level ownership versus section-only ownership
- acceptable temporary-binding use during framework-first delivery
- what makes a historical asset "strong enough" to proceed without generation

### `framework-first-delivery.md`

Make the framework milestone more explicit for website work:

- route shell complete
- navigation and footer working
- major layout bands present
- card/detail/list systems in place
- desktop and mobile behavior stable
- current imagery may still be provisional

### `mock-asset-pass.md`

Expand the template so it captures:

- route owner
- slot owner
- why each asset is sufficient for the current pass
- upgrade trigger
- residual visual risk

### `visual-source-inventory.md`

Consider adding fields for:

- authority reason
- replacement trigger
- route milestone supported

## Test Plan For The Later Implementation Pass

- `python -m unittest discover zero-to-website-design/tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

This plan is aligned if we agree on these points:

- the next skill pass should strengthen historical-mock framework delivery, not reopen broad visual ideation
- repo-owned images remain preferred over fresh generation when they are sufficient
- `temporary-binding` stays explicit and auditable
- framework-ready and delivery-ready remain distinct milestones
- usage docs should explicitly support "do not generate images yet"
- the package stays general-purpose and not blog-specific

## Suggested Next Step

If this direction looks right, the next implementation pass should:

1. revise the affected skill docs and references
2. tune the mock-asset templates
3. add or update regression tests for the new wording
4. run validation and production review
5. update project memory and ship the phase
