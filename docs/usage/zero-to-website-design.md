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

## Pre-Code Document Gate

Before broad implementation starts, the workflow should leave behind a compact durable artifact chain:

1. intake output or explicit assumptions
2. visual source map and source-path choice
3. design-system plus route-doc baseline
4. implementation map with milestone target and verification destination

Do not treat these as post-hoc paperwork. If the route inventory, deferred routes, source-path choice, milestone target, or implementation order only exist in chat, the workflow is still under-documented for broad editing.

## Continuity Gate

When work spans multiple sessions, preserve:

- current route slice
- weakest route evidence status
- temporary-binding assets still in control
- next QA or implementation target
- blocker owner
- handoff artifact or resume note

If a pass pauses while any required route is still blocked or unchecked, the next session should resume from the workstream or handoff rather than chat memory.

## Content Readiness

When placeholder, curated, generated-draft, or mixed content is still active:

- record content source status by route family
- name the route-family owner and metadata owner
- state whether framework-first delivery is still allowed
- record placeholder or draft replacement triggers
- treat unresolved content-source drift as a readiness limiter, not a hidden footnote

Framework-first delivery can still be valid with provisional content, but final delivery cannot overclaim past placeholder-brand drift, undefined ownership, or route/detail data mismatch.

## Route-Data Integrity

When routes are generated from data, the workflow should also preserve:

- route-data source of truth
- metadata source of truth
- feed/output source of truth when sitemap, RSS, robots, or similar outputs exist
- slug uniqueness and route identity checks
- explicit blocker ownership when rendered pages and exported outputs drift apart

Final delivery cannot overclaim past slug collisions, route-data mismatch, metadata mismatch, or feed/output drift.

## Route Specs

A touched core route should have a page spec or equivalent route doc that is strong enough for another session to answer:

- what the route is for
- which data source and metadata source power it
- whether feed/output relevance exists for that route family
- what QA evidence belongs to the route
- what still blocks the route and who owns the unblock
- what route-specific context must survive a handoff

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
7. Implement only after the visual source map, design docs, and implementation map exist.

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

## Generated Route Mockups

A chosen concept direction is not enough by itself when generated assets will guide implementation. Preserve:

- which routes must be expanded from the chosen concept before coding
- whether each generated route mockup inherits authority from the selected concept or comes from a route-specific pass
- which desktop/mobile coverage still remains unresolved
- whether the route mockup is only `temporary-binding` or strong enough for `binding-route`
- what another session must verify before implementation begins from that mockup

The next session should be able to read the visual-source artifacts and know exactly which generated route mockups exist, what they control, and what still blocks stronger authority.

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

## Asset Authority Continuity

When visual-source assets still control a route or section, preserve:

- which route family or route slice they own
- whether they are `Framework Ready` only, `Visual Delivery Ready`, or support only
- which provisional assets belong to the same upgrade queue
- what next verification or replacement step another session must run
- who owns the blocker or upgrade follow-up

A visual-source note should be enough for another session to resume the asset track without reconstructing the current upgrade state from chat.

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
- route evidence rows exist for touched core routes
- desktop screenshot QA
- mobile screenshot QA
- console, overflow, link, asset, and mobile-menu checks are recorded
- no page-level horizontal overflow
- key navigation links work
- mobile menu works when present
- local assets load
- known visual gaps are reported
- framework-ready versus visual-delivery-ready status is stated clearly
- temporary-binding ownership and upgrade triggers are stated when provisional imagery remains
- production review is run before final delivery

Final readiness claims must follow recorded route evidence: `not-checked` or `blocked` routes cannot support a ready claim, and `Framework Ready` must not be described as `Visual Delivery Ready`.


## Delivery Handoff

Final delivery artifacts should preserve the same authority detail as the earlier route, asset, and concept-to-mockup artifacts. When a pass is not fully final, record:

- the weakest route limiting reason
- whether generated route mockups still control any route family
- whether authority is inherited from a selected concept or is route-specific
- the active escalation target and next verification target

A handoff should be enough for another session to resume the delivery state without reconstructing the last verified authority from chat.
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
- updated asset-authority fields for route-family ownership, readiness limiter, and upgrade queue state

## When Not To Use

Use a narrower skill instead when:

- the task is a small component tweak
- the user only wants code review
- the project already has a project-specific screenshot fidelity skill
- the change is backend-only
