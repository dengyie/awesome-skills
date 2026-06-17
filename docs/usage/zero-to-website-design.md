# Zero-To-Website Design

`zero-to-website-design` is an end-to-end workflow for turning a blank or vague website request into a designed, implemented, QA-checked, delivery-ready site.

Use it when the user asks to:

- design a website from zero
- generate mockups before coding
- build from reference images or screenshots
- turn a loose idea into a blog, portfolio, landing page, product site, or docs site
- follow a disciplined visual-source-to-implementation process

## Install

From this repository:

```bash
mkdir -p ~/.agents/skills
cp -R zero-to-website-design ~/.agents/skills/
```

Restart or reload Codex so the skill list refreshes.

## First Prompt Examples

Blank brief:

```text
Use $zero-to-website-design to design and build a personal portfolio site from zero.
```

Reference-image workflow:

```text
Use $zero-to-website-design to turn these homepage and detail-page screenshots into a documented website implementation plan, then build it.
```

Generated concept workflow:

```text
Use $zero-to-website-design to generate three visual directions for this product site, let me choose one, then create route specs and implement it.
```

Generated route-owner workflow:

```text
Use $zero-to-website-design to generate route mockups for this site only if the repo's existing visuals are not strong enough to continue. Record why generation is needed, then map the chosen mockup to the route before implementation.
```

Historical mock workflow:

```text
Use $zero-to-website-design to rebuild this site from the historical PNG mockups already in the repo. Do not generate new images yet; first get the framework and route layout to a deliverable state.
```

## Workflow

The skill guides Codex through eleven gates:

1. Restore project context.
2. Run intake.
3. Collect visual sources.
4. Record visual provenance.
5. Choose the right source path.
6. Promote route owners into authoritative source material.
7. Write design docs before code.
8. Produce an implementation map.
9. Implement route by route.
10. Verify with build and browser QA.
11. Harden and deliver.

When the repository uses `.codex-memory/`, the workflow should also:

- restore current state before major work
- keep a bounded website workstream up to date
- append meaningful session progress
- promote durable delivery decisions
- generate a handoff when another session must resume

## Blank-Brief Path

When no strong reference exists, the skill should:

1. Ask only the minimum useful questions.
2. Infer reasonable defaults.
3. Generate or describe 3-4 distinct visual directions.
4. Wait for a selected direction before making it route-authoritative.
5. Expand the chosen direction into route specs.
6. Record why generation was needed instead of stronger existing visuals.
7. Implement only after the visual source map and design docs exist.

## Reference-Image Path

When screenshots, mockups, or Figma exports already exist, the skill should:

1. Inspect the provided references.
2. Record the source method and authority of each image.
3. Separate exploratory images from binding implementation references.
4. Map each binding reference to routes, sections, and viewports.
5. Implement against the route-specific references first.

## Historical-Mock Path

When the repo already contains useful design images, archived mockups, or approved screenshots, the skill should:

1. Inventory project-owned visual sources before generating anything new.
2. Classify them with provenance and authority.
3. Decide whether each asset is strong enough for `Framework Ready`, `Visual Delivery Ready`, or only supporting texture.
4. Use `temporary-binding` only when the current stage is framework-first delivery.
5. Record route owner, section or slot owner, what each asset controls, and what still needs to be upgraded later.
6. Keep temporary asset usage visible in design docs and final handoff notes.

## Generated-Authority Path

When generation is justified, the skill should:

1. Record why repo-owned or historical visuals were insufficient.
2. Keep newly generated images `exploratory` until they are concrete enough for user or route selection.
3. Promote them to `candidate`, `approved-direction`, `temporary-binding`, or `binding-route` only with explicit ownership and milestone records.
4. Record replacement triggers for any generated image that owns a route during implementation.
5. Retire replaced generated images as `obsolete` instead of silently overwriting the authority trail.

## Visual Provenance

This skill treats image origin as a first-class requirement.

Every visual source should be classified as:

- `exploratory`
- `candidate`
- `approved-direction`
- `binding-route`
- `temporary-binding`
- `obsolete`

Each binding image should record:

- path or URL
- source method
- date
- route or section ownership
- viewport
- limitations

Recognized source methods should include historical project inputs such as `existing-project-mockup`.

This prevents concept art, generated mockups, screenshots, and final acceptance images from being mixed accidentally.

## Project Documents

When the project lacks equivalent docs, the skill uses templates from `zero-to-website-design/assets/templates/`:

- `design-system-master.md`
- `implementation-plan.md`
- `asset-and-data-spec.md`
- `page-spec.md`
- `visual-source-map.md`
- `visual-source-inventory.md`
- `mock-asset-pass.md`
- `website-workstream.md`
- `qa-report.md`

These should be copied into the target project and filled in. Do not leave placeholders as final documentation.

## QA Expectations

The workflow is not complete just because the build passes.

Minimum verification:

- build or typecheck command passes
- desktop screenshot QA
- mobile screenshot QA
- no page-level horizontal overflow
- key navigation links work
- mobile menu works when present
- local assets load
- known visual gaps are reported
- framework-ready versus visual-delivery-ready status is stated clearly
- temporary-binding ownership and upgrade triggers are stated when provisional imagery remains
- production review is run before final delivery

## Project Memory

When `best-project-memory` is available, `zero-to-website-design` should act like a governance-aware consumer rather than a read-only guest.

Typical memory behavior:

- read `project-state.md` and `todo.md` before major delivery work
- keep route or delivery effort in a dedicated workstream such as `website-delivery.md` or `visual-qa-pass.md`
- append a session entry after meaningful implementation or QA progress
- promote binding source-path or asset-strategy decisions
- generate a handoff when the website pass pauses midstream

Template support now includes:

- `website-workstream.md` for a reusable delivery workstream artifact
- updated implementation/QA/page-spec templates that record framework-ready versus delivery-ready state
- updated visual source map language for `binding-route` and `temporary-binding`

## When Not To Use

Use a narrower skill instead when:

- the task is a small component tweak
- the user only wants code review
- the project already has a project-specific screenshot fidelity skill
- the change is backend-only
