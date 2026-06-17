---
name: zero-to-website-design
description: Use when creating a complete website from a blank or vague starting point, turning user goals, visual references, screenshots, historical repo mockups, or generated concept images into design-system docs, route/page specs, implementation, browser visual QA, and delivery readiness. Especially useful when the user asks to design from zero, generate mockups before implementation, build from reference images, rebuild from historical project PNGs, ship framework-first before final artwork, or explicitly says not to generate new images yet.
---

# Zero-To-Website Design

## Mission

Build complete websites from zero with explicit visual sources, documented design decisions, route-level implementation plans, screenshot-based QA, and production delivery gates.

Do not treat "looks nice" or "build passed" as completion. A website is ready only when the visual source, implementation, responsive behavior, content/data source, and delivery path have all been checked.

Historical repo images are first-class inputs. When a project already has usable mockups, screenshots, or concept PNGs, use them to drive a framework-ready pass before reaching for new image generation.

## Required Workflow

1. Restore project context.
   - If the project has memory, agent, design-system, README, or planning files, read them before deciding what to build.
   - Preserve existing project conventions unless they block the requested design outcome.

2. Run intake.
   - If the brief is vague, read `references/intake-brief.md`.
   - Ask only for decisions that materially change the result. Otherwise make reasonable assumptions and record them.

3. Collect visual sources.
   - Inspect repo-owned assets, historical mockups, screenshots, or user-provided references before deciding that new generation is needed.
   - If the user says not to generate new images yet, treat the best available project-owned visuals as the default source path for the current pass.
   - If the user has no usable binding or temporary visual sources, read `references/concept-generation.md` and create concept directions before implementation.

4. Record visual provenance.
   - Read `references/visual-provenance.md` before treating any image as a source of truth.
   - Classify each reference as `exploratory`, `candidate`, `approved-direction`, `binding-route`, `temporary-binding`, or `obsolete`.

5. Choose the right source path.
   - Prefer repo-owned final assets or approved user references first.
   - Use historical mock assets when they are strong enough for framework or route composition.
   - Use local structural mock assets when final imagery is not ready but framework delivery should continue.
   - Do not generate new concepts when repo-owned images already provide enough route authority for the current milestone.
   - Generate new concepts only when the project still lacks enough authority to proceed.

6. Promote route owners into authoritative source material.
   - Map each `binding-route` or `temporary-binding` reference to routes, sections, and viewports.
   - Record whether each temporary asset controls whole-route composition, section composition, illustration slot shape, or only palette/texture.
   - Never mix exploratory concept images with final acceptance images without saying so.
   - Read `references/historical-mock-pass.md` when historical visuals drive the current pass.

7. Write design docs before code.
   - Read `references/design-system-docs.md`.
   - Use the templates in `assets/templates/` when the project lacks equivalent docs.

8. Produce an implementation map.
   - Read `references/implementation-map.md`.
   - Map visual regions to components, routes, assets, data sources, and responsive behavior before editing.
   - Record route owner, asset-slot owner, milestone target, and upgrade trigger when temporary-binding assets are involved.

9. Implement route by route.
   - Read `references/framework-first-delivery.md` when the project should stop at a framework milestone before final asset polish.
   - Build the site framework first: layout, navigation, core routes, card systems, responsive rhythm, and local assets.
   - Prefer project-owned assets over hotlinked assets.
   - Keep content placeholder or curated when the user wants framework-first delivery.
   - Treat `Framework Ready` as a valid milestone when layout, interaction, and responsive structure are correct even if final bespoke art is not ready yet.
   - Keep `temporary-binding` assets explicit in docs and delivery notes.

10. Verify with build and browser QA.
   - Run the project's build or typecheck command.
   - Read `references/route-acceptance.md` and `references/visual-qa-checklist.md`.
   - Use browser/Playwright QA for desktop and mobile screenshots, overflow checks, link checks, menu states, and asset loading.

11. Harden and deliver.
   - Read `references/production-delivery.md`.
   - Use a production review skill when available before publishing or final signoff.
   - Report routes touched, source references used, files changed, verification results, framework-ready versus delivery-ready status, and known visual gaps.

12. Integrate project memory when the work is long-running.
   - Read `references/project-memory-integration.md` when the repository uses `.codex-memory/`.
   - Update the relevant workstream, `todo.md`, and `session-log.md` after meaningful progress.
   - Promote durable delivery decisions when the source path, route status, or asset strategy becomes binding.
   - Generate a handoff when the work pauses midstream or another session must resume delivery.

## Reference Routing

- `references/intake-brief.md`: read when the user starts with a vague idea or incomplete product/site definition.
- `references/concept-generation.md`: read when visual direction or route mockups need to be generated.
- `references/historical-mock-pass.md`: read when repo-owned historical visuals or archived mockups should drive the current pass.
- `references/visual-provenance.md`: read before any image becomes authoritative.
- `references/design-system-docs.md`: read before creating or updating design docs.
- `references/implementation-map.md`: read before code changes.
- `references/route-acceptance.md`: read before implementing or reviewing route types.
- `references/visual-qa-checklist.md`: read before signoff.
- `references/framework-first-delivery.md`: read when framework-first delivery is an explicit milestone.
- `references/project-memory-integration.md`: read when the repository uses `.codex-memory/` and the work spans multiple sessions.
- `references/production-delivery.md`: read before deploy, publish, PR, or final handoff.

## Template Routing

Use these files as copyable project scaffolds when equivalent files do not already exist:

- `assets/templates/design-system-master.md`
- `assets/templates/implementation-plan.md`
- `assets/templates/asset-and-data-spec.md`
- `assets/templates/page-spec.md`
- `assets/templates/visual-source-map.md`
- `assets/templates/visual-source-inventory.md`
- `assets/templates/mock-asset-pass.md`
- `assets/templates/website-workstream.md`
- `assets/templates/qa-report.md`

Adapt templates to the project. Do not copy placeholders into final deliverables without filling them in.

## Completion Standard

A zero-to-website pass is complete only when:

- the project brief and assumptions are documented
- the visual source map identifies image origins and authority
- design-system and route docs exist or have been updated
- core routes are implemented responsively
- any framework-first milestone is explicitly labeled as such
- temporary-binding route owners and upgrade triggers are documented when provisional imagery remains
- local or owned assets are used where possible
- build/typecheck passes
- desktop and mobile browser QA have been run
- production readiness has been reviewed
- known gaps are explicitly reported
