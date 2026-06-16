# Zero-To-Website Design Skill Plan

> Status: Implemented as `zero-to-website-design/` v1 draft package.

## Goal

Create a reusable Codex skill that can take a website project from zero or vague direction to a complete, shippable design implementation.

The skill should encode the workflow proven by the Little Lighthouse Folk Canvas rebuild:

1. Establish project memory and constraints.
2. Convert a loose visual preference into concrete concept directions.
3. Generate or collect reference images and record their provenance.
4. Promote selected images into binding design source material.
5. Produce design-system and page-level implementation documents before coding.
6. Implement the site structure and visual system route by route.
7. Use browser screenshots and Playwright checks to iterate against the reference images.
8. Run production-readiness review before delivery or publish.

The core promise is not "make a nice page." It is "build a coherent website from scratch with explicit visual sources, design documents, implementation gates, and visual QA."

## Proposed Skill Name

`zero-to-website-design`

Alternative names:

- `website-design-from-zero`
- `complete-website-design`
- `visual-website-builder`

Recommendation: use `zero-to-website-design` because it matches the user's wording and makes the trigger intent clear.

## Target Users And Triggers

Use this skill when the user asks for work like:

- "从 0 开始设计一个网站"
- "帮我搭一个完整网站"
- "根据参考图做一个网站"
- "先生成设计图, 再按图实现"
- "我只有一个想法, 你帮我做成网站"
- "按照这次 Folk Canvas 的流程做一个新项目"
- "做一个能上线的个人博客/作品集/产品官网/文档站"

Do not use this skill for:

- Small component-only tweaks.
- Pure code review.
- Backend-only features.
- Pixel-fidelity implementation when the user already has a project-specific screenshot fidelity skill. In that case, use the project-specific skill.

## Relationship To Other Skills

This should be an orchestrating skill. It should call out related skills when available, but not require all of them to exist.

Recommended chain:

1. `best-project-memory`
   - Use first when working inside an existing project with memory files or project rules.
   - Store decisions, current objective, TODOs, and session summaries.

2. `imagegen`
   - Use when the project lacks strong visual references.
   - Generate concept boards, homepage mockups, and route-specific mockups.
   - Record which generated images are exploratory and which are binding.

3. `frontend-design`
   - Use for high-quality UI composition, interaction states, responsive behavior, and design-system judgment.

4. `playwright-interactive`
   - Use after implementation changes.
   - Capture desktop and mobile screenshots.
   - Check layout overflow, interaction states, clickable navigation, asset rendering, and visual gaps.

5. `production-code-quality-review`
   - Use before final delivery.
   - Catch source-of-truth drift, duplicated data, route/export mismatch, accessibility gaps, and maintainability risks.

6. Deployment skill or platform plugin
   - Use only after the site passes build, visual QA, and production review.

## Skill Package Shape

Proposed folder:

```text
zero-to-website-design/
  SKILL.md
  agents/
    openai.yaml
  references/
    intake-brief.md
    visual-provenance.md
    concept-generation.md
    design-system-docs.md
    implementation-map.md
    route-acceptance.md
    visual-qa-checklist.md
    production-delivery.md
  assets/
    templates/
      design-system-master.md
      implementation-plan.md
      asset-and-data-spec.md
      page-spec.md
      visual-source-map.md
      qa-report.md
```

No scripts are required for v1. The workflow is mostly procedural and project-dependent. Add scripts later only if repeated validation tasks become deterministic enough to automate.

## Skill Design Principles

### 1. Make visual source explicit

The skill must never treat generated images, screenshots, Figma exports, moodboards, and live references as interchangeable.

Every visual reference should be classified:

- `exploratory`: useful for direction, not binding.
- `candidate`: user may choose it.
- `approved`: user selected it as direction.
- `binding`: implementation must match it.
- `obsolete`: retained for history, not used for implementation.

Each binding image should record:

- file path or URL
- creation method: imagegen, Figma export, screenshot, user upload, manual design, other
- creation date
- route or section ownership
- viewport represented
- whether mobile and desktop are both covered
- known limitations

This is the missing piece in `folk-canvas-fidelity`: that skill lists which PNGs are source of truth, but it does not explain how the PNGs were produced. This new skill should make provenance first-class.

### 2. Design docs before code

Before implementation, the agent should write compact project docs:

- `design-system/MASTER.md`
- `design-system/IMPLEMENTATION-PLAN.md`
- `design-system/ASSET-AND-DATA-SPEC.md`
- `design-system/pages/<route>.md`
- optional `design-system/VISUAL-SOURCE-MAP.md`

These docs should define:

- brand name and tone
- target audience
- page inventory
- visual language
- typography hierarchy
- color tokens
- layout primitives
- asset requirements
- route-specific acceptance criteria
- implementation phases
- QA gate

The skill should discourage immediate coding when the visual direction is still undefined.

### 3. Implement framework before content perfection

For new websites, the first delivery should prioritize:

- route structure
- layout frame
- navigation
- card systems
- responsive behavior
- visual rhythm
- placeholder or curated content where acceptable
- static export or deployment compatibility

Content authenticity can be refined later unless the user specifically asks for production content first.

### 4. Prefer project-owned assets

For shippable implementations:

- Avoid hotlinked images unless the user explicitly chooses them.
- Use local assets, generated bitmap assets, SVGs, CSS primitives, or user-provided files.
- Track asset role and source.
- Verify images load in exported or deployed output.

### 5. Screenshot QA is mandatory

The skill should not allow "build passed" to mean "design is done."

Minimum QA matrix:

- desktop: 1440x900 or 1600x900
- mobile: 390x844
- all primary routes
- mobile menu open/close if present
- key links and calls to action
- `document.documentElement.scrollWidth <= document.documentElement.clientWidth`
- no clipped text
- no incoherent overlap
- no broken local assets

For reference-image work, the final report must include known visual gaps.

## Proposed `SKILL.md` Outline

```md
---
name: zero-to-website-design
description: Use when creating a complete website from a blank or vague starting point, turning user goals, references, or generated concept images into design-system docs, route/page specs, implementation, browser visual QA, and delivery readiness. Especially useful when the user asks to design from zero, generate mockups first, implement from reference images, or build a shippable personal site, blog, portfolio, product site, or documentation site.
---

# Zero-To-Website Design

## Mission
Build complete websites from zero with explicit design sources, documented visual decisions, route-level implementation plans, and screenshot-based QA.

## Required Workflow
1. Restore project context.
2. Run intake.
3. Create or collect visual references.
4. Record visual provenance.
5. Promote approved references into binding source material.
6. Write design docs before code.
7. Implement route by route.
8. Verify with build and Playwright.
9. Run production readiness review.
10. Report delivery status and known gaps.

## Reference Routing
- Read `references/intake-brief.md` when the brief is vague.
- Read `references/concept-generation.md` when images or concepts need to be generated.
- Read `references/visual-provenance.md` before treating any image as source of truth.
- Read `references/design-system-docs.md` before writing project docs.
- Read `references/implementation-map.md` before coding.
- Read `references/route-acceptance.md` for route-specific gates.
- Read `references/visual-qa-checklist.md` before signoff.
- Read `references/production-delivery.md` before deploy or final handoff.
```

## Proposed Reference Files

### `references/intake-brief.md`

Purpose: help the agent turn a vague request into a usable project brief without over-questioning.

Should include:

- minimum viable questions
- assumptions the agent can make
- site type taxonomy
- audience and workflow prompts
- deliverable definition
- constraints checklist

Key rule: ask only when needed; otherwise proceed with reasonable defaults and document assumptions.

### `references/concept-generation.md`

Purpose: guide image and visual direction creation.

Should include:

- when to use `imagegen`
- how many concepts to generate
- how to prompt for desktop/mobile frames
- how to create route-specific mockups after a concept is chosen
- how to avoid generic AI UI
- how to mark concept images as exploratory vs binding

Recommended flow:

1. Generate 3-4 direction concepts.
2. Let user choose one.
3. Extend chosen direction to core routes.
4. Create a visual source map.
5. Only then implement.

### `references/visual-provenance.md`

Purpose: prevent confusion about where images came from and which images control implementation.

Should include:

- image classification table
- source tracking template
- route ownership matrix
- approval status rules
- stale-image handling

Template:

```md
| Asset | Source Method | Date | Status | Controls | Notes |
| --- | --- | --- | --- | --- | --- |
| output/design/homepage.png | imagegen | 2026-06-17 | binding | `/` desktop/mobile | User selected concept A |
```

### `references/design-system-docs.md`

Purpose: define the documents that must exist before coding.

Should include:

- `MASTER.md` structure
- `IMPLEMENTATION-PLAN.md` structure
- `ASSET-AND-DATA-SPEC.md` structure
- per-route page spec structure
- acceptance gate language

This reference should encode the same habit that worked in Folk Canvas: write the visual contract first, then implement against it.

### `references/implementation-map.md`

Purpose: translate reference images and design docs into code edits.

Should include:

- map mockup regions to components
- identify shared primitives
- identify data and asset needs
- decide route order
- define desktop/mobile differences
- preserve existing project conventions
- avoid unrelated refactors

### `references/route-acceptance.md`

Purpose: route-level quality gates.

Should include generic acceptance checklists for:

- homepage
- listing/index page
- detail page
- category/filter/archive page
- about/landing page
- docs/content page

Each checklist should cover:

- layout regions
- navigation
- responsive behavior
- empty/loading states when relevant
- accessibility
- assets
- metadata

### `references/visual-qa-checklist.md`

Purpose: browser verification before signoff.

Should include:

- build command first
- local preview strategy
- desktop and mobile viewport list
- screenshot naming
- overflow checks
- interaction checks
- image load checks
- console error checks
- known gap report

### `references/production-delivery.md`

Purpose: final hardening before publishing.

Should include:

- production code review handoff
- SEO and metadata checks
- sitemap/RSS/data-source consistency
- static export or deployment checks
- no rejected placeholder branding
- no broken generated assets
- final user report structure

## Development Tasks

### Task 1: Create the skill skeleton

Files:

- Create: `zero-to-website-design/SKILL.md`
- Create: `zero-to-website-design/agents/openai.yaml`
- Create: `zero-to-website-design/references/*.md`
- Create: `zero-to-website-design/assets/templates/*.md`

Steps:

- [x] Use `skill-creator` initialization flow if creating the actual package.
- [x] Keep `SKILL.md` concise and procedural.
- [x] Put detailed templates and checklists in references/assets.
- [x] Generate `agents/openai.yaml` from the final `SKILL.md`.

### Task 2: Write the core workflow

Files:

- Modify: `zero-to-website-design/SKILL.md`
- Create: `zero-to-website-design/references/intake-brief.md`
- Create: `zero-to-website-design/references/visual-provenance.md`
- Create: `zero-to-website-design/references/concept-generation.md`

Steps:

- [x] Define the trigger description clearly.
- [x] Encode the 10-step design-to-delivery workflow.
- [x] Add routing rules for when to read each reference.
- [x] Add provenance rules for generated, uploaded, screenshot, and Figma images.

### Task 3: Add design documentation templates

Files:

- Create: `zero-to-website-design/assets/templates/design-system-master.md`
- Create: `zero-to-website-design/assets/templates/implementation-plan.md`
- Create: `zero-to-website-design/assets/templates/asset-and-data-spec.md`
- Create: `zero-to-website-design/assets/templates/page-spec.md`
- Create: `zero-to-website-design/assets/templates/visual-source-map.md`

Steps:

- [x] Make templates compact enough to be useful in real projects.
- [x] Include visual-source and route-acceptance fields.
- [x] Include known-gaps and assumptions sections.
- [x] Avoid overfitting to Little Lighthouse or Folk Canvas.

### Task 4: Add implementation and QA references

Files:

- Create: `zero-to-website-design/references/design-system-docs.md`
- Create: `zero-to-website-design/references/implementation-map.md`
- Create: `zero-to-website-design/references/route-acceptance.md`
- Create: `zero-to-website-design/references/visual-qa-checklist.md`
- Create: `zero-to-website-design/references/production-delivery.md`

Steps:

- [x] Encode route-by-route implementation order.
- [x] Add browser QA gates.
- [x] Add production-review gate.
- [x] Add final signoff format.

### Task 5: Validate and forward-test

Files:

- Modify if needed: `zero-to-website-design/SKILL.md`
- Modify if needed: `zero-to-website-design/references/*.md`
- Modify if needed: `zero-to-website-design/assets/templates/*.md`

Steps:

- [x] Run skill validation.
- [x] Test the skill on one hypothetical blank blog request.
- [x] Test the skill on one "I have reference images" request.
- [x] Check that the skill does not force image generation when the user already has references.
- [x] Check that provenance prevents mixing exploratory and binding images.

## Implementation Results

Created `zero-to-website-design/` as a v1 draft skill package:

- `SKILL.md` contains the concise trigger surface and ten-step workflow.
- `agents/openai.yaml` provides UI metadata.
- `references/` contains intake, concept generation, provenance, design docs, implementation mapping, route acceptance, visual QA, and production delivery guidance.
- `assets/templates/` contains reusable Markdown scaffolds for design-system docs, implementation plans, asset/data specs, page specs, visual source maps, and QA reports.

Validation and review:

- `quick_validate.py zero-to-website-design` passes.
- `python -m unittest discover production-code-quality-review/tests -v` passes with three Windows-only environment skips.
- `production-code-quality-review` review flow was run via `review-entrypoint.py --repo . --format markdown`.
- Review follow-up fixed README install discoverability for the new package.
- Review follow-up fixed Windows path normalization in `production-code-quality-review/scripts/review_skill_lib.py`.
- Review follow-up made Windows-only symlink/POSIX install helper constraints explicit in tests.

Forward-test notes:

- Blank-site request path is covered by `intake-brief.md`, `concept-generation.md`, design-system templates, and QA gates.
- Existing-reference request path is covered by `visual-provenance.md`, `visual-source-map.md`, and route/page specs without forcing image generation.
- Provenance distinguishes `exploratory`, `candidate`, `approved`, `binding`, and `obsolete`, addressing the missing image-origin gap found in the Folk Canvas project-specific skill.

## Acceptance Criteria

The v1 skill is acceptable when:

- A new Codex session can understand when to trigger it from frontmatter alone.
- `SKILL.md` stays focused and does not become a giant design textbook.
- The workflow requires design docs before implementation.
- The workflow distinguishes image generation from image authority.
- The workflow supports both "no references yet" and "user provided reference images."
- The workflow requires browser screenshot QA before signoff.
- The workflow includes production review before deployment.
- The skill can be used outside the Little Lighthouse project.
- Validation passes.

## Open Questions For Alignment

1. Should the first release be English-only like the existing repo docs, or should this skill include Chinese usage docs too?
2. Should the skill package include reusable Markdown templates in `assets/templates/`, or keep them in `references/` only?
3. Should `imagegen` be recommended but optional, or should this skill require image generation when starting from zero?
4. Should the skill target static websites first, or also cover full web apps with authenticated/product workflows?
5. Should we add a small validation script later to check that a project has design docs, visual-source map, screenshots, and QA report before delivery?

## Initial Recommendation

Build v1 as a general orchestrating skill:

- English `SKILL.md` and references for broad reuse.
- Optional Chinese user docs can be added under `docs/zh/` after the skill stabilizes.
- Keep `imagegen` optional but strongly recommended when the user has no binding references.
- Include templates as assets because they are output scaffolds, not instructions that always need to enter context.
- Avoid scripts in v1; add them only after the workflow has repeated enough to reveal deterministic checks.
