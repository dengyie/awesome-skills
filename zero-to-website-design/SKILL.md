---
name: zero-to-website-design
description: Use when creating a complete website from a blank or vague starting point, turning user goals, visual references, screenshots, or generated concept images into design-system docs, route/page specs, implementation, browser visual QA, and delivery readiness. Especially useful when the user asks to design from zero, generate mockups before implementation, build from reference images, or ship a personal site, blog, portfolio, product site, landing page, or documentation site.
---

# Zero-To-Website Design

## Mission

Build complete websites from zero with explicit visual sources, documented design decisions, route-level implementation plans, screenshot-based QA, and production delivery gates.

Do not treat "looks nice" or "build passed" as completion. A website is ready only when the visual source, implementation, responsive behavior, content/data source, and delivery path have all been checked.

## Required Workflow

1. Restore project context.
   - If the project has memory, agent, design-system, README, or planning files, read them before deciding what to build.
   - Preserve existing project conventions unless they block the requested design outcome.

2. Run intake.
   - If the brief is vague, read `references/intake-brief.md`.
   - Ask only for decisions that materially change the result. Otherwise make reasonable assumptions and record them.

3. Create or collect visual references.
   - If the user has no binding references, read `references/concept-generation.md` and create concept directions before implementation.
   - If the user provides screenshots, mockups, Figma exports, or live-site references, inspect them before editing.

4. Record visual provenance.
   - Read `references/visual-provenance.md` before treating any image as a source of truth.
   - Classify each reference as exploratory, candidate, approved, binding, or obsolete.

5. Promote approved references into binding source material.
   - Map each binding reference to routes, sections, and viewports.
   - Never mix exploratory concept images with final acceptance images without saying so.

6. Write design docs before code.
   - Read `references/design-system-docs.md`.
   - Use the templates in `assets/templates/` when the project lacks equivalent docs.

7. Produce an implementation map.
   - Read `references/implementation-map.md`.
   - Map visual regions to components, routes, assets, data sources, and responsive behavior before editing.

8. Implement route by route.
   - Build the site framework first: layout, navigation, core routes, card systems, responsive rhythm, and local assets.
   - Prefer project-owned assets over hotlinked assets.
   - Keep content placeholder or curated when the user wants framework-first delivery.

9. Verify with build and browser QA.
   - Run the project's build or typecheck command.
   - Read `references/route-acceptance.md` and `references/visual-qa-checklist.md`.
   - Use browser/Playwright QA for desktop and mobile screenshots, overflow checks, link checks, menu states, and asset loading.

10. Harden and deliver.
   - Read `references/production-delivery.md`.
   - Use a production review skill when available before publishing or final signoff.
   - Report routes touched, source references used, files changed, verification results, and known visual gaps.

## Reference Routing

- `references/intake-brief.md`: read when the user starts with a vague idea or incomplete product/site definition.
- `references/concept-generation.md`: read when visual direction or route mockups need to be generated.
- `references/visual-provenance.md`: read before any image becomes authoritative.
- `references/design-system-docs.md`: read before creating or updating design docs.
- `references/implementation-map.md`: read before code changes.
- `references/route-acceptance.md`: read before implementing or reviewing route types.
- `references/visual-qa-checklist.md`: read before signoff.
- `references/production-delivery.md`: read before deploy, publish, PR, or final handoff.

## Template Routing

Use these files as copyable project scaffolds when equivalent files do not already exist:

- `assets/templates/design-system-master.md`
- `assets/templates/implementation-plan.md`
- `assets/templates/asset-and-data-spec.md`
- `assets/templates/page-spec.md`
- `assets/templates/visual-source-map.md`
- `assets/templates/qa-report.md`

Adapt templates to the project. Do not copy placeholders into final deliverables without filling them in.

## Completion Standard

A zero-to-website pass is complete only when:

- the project brief and assumptions are documented
- the visual source map identifies image origins and authority
- design-system and route docs exist or have been updated
- core routes are implemented responsively
- local or owned assets are used where possible
- build/typecheck passes
- desktop and mobile browser QA have been run
- production readiness has been reviewed
- known gaps are explicitly reported

