---
name: zero-to-website-design
description: Use when creating a complete website from a blank or vague starting point, turning user goals, visual references, screenshots, historical repo mockups, or generated concept images into design-system docs, route/page specs, implementation, browser visual QA, and delivery readiness. Especially useful when the user asks to design from zero, generate mockups before implementation, build from reference images, rebuild from historical project PNGs, fix a page that differs too much from a design image, ship framework-first before final artwork, or explicitly says not to generate new images yet.
---

# Zero-To-Website Design

## Mission

Build complete websites from zero with explicit visual sources, documented design decisions, route-level implementation plans, screenshot-based QA, and production delivery gates.

Do not treat "looks nice" or "build passed" as completion. A website is ready only when the visual source, implementation, responsive behavior, content/data source, and delivery path have all been checked.

Historical repo images are first-class inputs. When a project already has usable mockups, screenshots, or concept PNGs, use them to drive a framework-ready pass before reaching for new image generation.

## Required Workflow

1. Restore project context and define the website milestone.
   - If the project has memory, agent, design-system, README, or planning files, read them before deciding what to build.
   - Preserve existing project conventions unless they block the requested design outcome.
   - Define the current website milestone before design or implementation starts.
   - Classify work as `P0`, `P1`, `P2/P3`, or `Manual-required`.
   - Execute only P0/P1 work for this milestone. Put polish, extra routes, future artwork, and long-term design-system improvements into backlog unless they block current acceptance.
   - Output and obey the milestone contract: milestone, goal, P0/P1 scope, out-of-scope P2/P3, manual-required, phase limit, phase split, acceptance criteria, and stop conditions.
   - Use at most 3 phases by default and at most 5 for genuinely complex sites. Do not start a new milestone automatically after the current one is accepted.

2. Run intake.
   - If the brief is vague, read `references/intake-brief.md`.
   - Ask only for decisions that materially change the result. Otherwise make reasonable assumptions and record them.
   - Treat the user's visual direction choice as a material decision for from-zero websites, brand sites, portfolios, landing pages, product pages, and any task whose final look matters. Do not assume it from text mood words.
   - Preserve a compact intake output or equivalent assumptions before concept expansion or broad implementation begins.

3. Collect visual sources.
   - Inspect repo-owned assets, historical mockups, screenshots, or user-provided references before deciding that new generation is needed.
   - If the user says not to generate new images yet, treat the best available project-owned visuals as the default source path for the current pass.
   - If generation is still chosen, record why existing source paths were insufficient for this milestone.
   - If the user has no usable binding or temporary visual sources, read `references/concept-generation.md`, create 2-4 candidate visual directions or homepage mockups, show them to the user, and wait for the user to choose or combine a direction before visual implementation.
   - Do not start a `Visual Delivery Ready` implementation from a text-only direction, internal taste, or unselected concept. Without user-selected visual authority, the milestone can only target `Framework Ready`, and the final report must say that visual direction selection remains open.

4. Record visual provenance.
   - Read `references/visual-provenance.md` before treating any image as a source of truth.
   - Classify each reference as `exploratory`, `candidate`, `approved-direction`, `binding-route`, `temporary-binding`, or `obsolete`.
   - Do not promote any generated or collected direction above `candidate` until the user explicitly selects it. A text description alone is not `approved-direction`.

5. Choose the right source path.
   - Prefer repo-owned final assets or approved user references first.
   - Use historical mock assets when they are strong enough for framework or route composition.
   - Use local structural mock assets when final imagery is not ready but framework delivery should continue.
   - Do not generate new concepts when repo-owned images already provide enough route authority for the current milestone.
   - Explicit user request can justify generation, but it does not bypass source-path evaluation or provenance recording.
   - Generate new concepts only when the project still lacks enough authority to proceed.

6. Promote route owners into authoritative source material.
   - Map each `binding-route` or `temporary-binding` reference to routes, sections, and viewports.
   - For from-zero sites, promote route owners only after the user-selected direction is recorded. If no user-selected visual direction exists, route owners may support framework structure but must not be used to claim final visual signoff.
   - Record whether each temporary asset controls whole-route composition, section composition, illustration slot shape, or only palette/texture.
   - For generated route owners, record milestone supported and replacement trigger before implementation begins.
   - Never mix exploratory concept images with final acceptance images without saying so.
   - Read `references/historical-mock-pass.md` when historical visuals drive the current pass.

7. Write design docs before code.
   - Read `references/design-system-docs.md`.
   - Do not treat design docs as post-hoc cleanup. Broad implementation starts only after the intake output, route inventory, source-path choice, and milestone target are visible in project docs.
   - Use the templates in `assets/templates/` when the project lacks equivalent docs.

8. Run the design fidelity setup for binding references.
   - Read `references/design-fidelity-loop.md` whenever a design screenshot, mockup, generated route mockup, Figma export, or historical image should control the page.
   - Do not treat binding references as mood boards or palettes. If the page only reuses colors, fonts, or rounded corners while missing the reference layout, component silhouettes, decorative assets, and hierarchy, the fidelity pass has failed.
   - Do not satisfy a binding route by placing the whole reference screenshot on the page, using it as a full-page background, or layering transparent hotspots over it. Rebuild the selected image as real DOM, components, local assets, and interactions.
   - Decompose each binding reference into layout, typography, color, spacing, component, asset, and responsive facts before implementation.
   - Create a page-by-page, item-by-item fidelity audit for every binding route before claiming visual readiness. Compare each route's hero, navigation, sections, cards, typography blocks, asset slots, decorative resources, spacing, and responsive states against the design image.
   - Define the fidelity budget: blocking deviations, accepted gaps, and out-of-scope viewports or states.
   - If existing assets cannot reproduce the reference, create UI asset or component prompt records before generation. Generate necessary UI images, illustrations, textures, icons, or panels only when they support the binding route.
   - Plan implementation screenshot paths, side-by-side comparison evidence, deviation backlog, and the fix loop before coding.

9. Produce an implementation map.
   - Read `references/implementation-map.md`.
   - Treat the implementation map as a pre-code gate, not an after-action summary.
   - Map visual regions to components, routes, assets, data sources, and responsive behavior before editing.
   - Record route owner, asset-slot owner, milestone target, and upgrade trigger when temporary-binding assets are involved.

10. Implement route by route.
   - Read `references/framework-first-delivery.md` when the project should stop at a framework milestone before final asset polish.
   - Build the site framework first: layout, navigation, core routes, card systems, responsive rhythm, and local assets.
   - When a binding design image exists, implement against the reference decomposition instead of broad visual memory.
   - Implement binding references as interactive page structure: text remains text, buttons and links are real controls, cards and sections are components, and charts or diagrams are built with code or fit-for-purpose local assets.
   - Draw, code, or generate the missing UI assets and component-shaped resources needed to reproduce the reference instead of substituting generic cards or stock-like sections.
   - Prefer project-owned assets over hotlinked assets.
   - Keep content placeholder or curated when the user wants framework-first delivery.
   - Treat `Framework Ready` as a valid milestone when layout, interaction, and responsive structure are correct even if final bespoke art is not ready yet.
   - Keep `temporary-binding` assets explicit in docs and delivery notes.

11. Verify with build, browser QA, and screenshot fidelity checks.
   - Run the project's build or typecheck command.
   - Read `references/route-acceptance.md` and `references/visual-qa-checklist.md`.
   - Use browser/Playwright QA for desktop and mobile screenshots, overflow checks, link checks, menu states, and asset loading.
   - For binding references, capture implementation screenshot evidence at matching viewports, compare side-by-side with the design screenshot, record the difference summary, and fix blocking visual deviations.
   - For each binding route, complete the itemized fidelity audit row by row. A route with unchecked design items, missing implementation evidence, or unresolved blocking item mismatches cannot be `Visual Delivery Ready`.
   - Record route evidence rows before claiming `Framework Ready` or `Visual Delivery Ready`.

12. Harden and deliver.
   - Read `references/production-delivery.md`.
   - Use a production review skill when available before publishing or final signoff.
   - At each phase end, run a phase-gate review when available and fix only P0/P1 blockers for the current milestone.
   - Move non-blocking suggestions to backlog and external gaps to `Manual-required`.
   - Stop after the current milestone's P0/P1 acceptance criteria pass necessary verification; do not continue into additional design polish or the next milestone.
   - Report routes touched, source references used, files changed, verification results, framework-ready versus delivery-ready status, and known visual gaps.
   - If the user did not choose from visual direction images or route mockups, explicitly state that the result is `Framework Ready` only and that final visual direction remains unapproved.
   - Do not claim visual parity unless the fidelity pass includes reference decomposition, implementation screenshot, comparison evidence, and no unresolved blocking visual deviations.

13. Integrate project memory when the work is long-running.
   - Read `references/project-memory-integration.md` when the repository uses `.codex-memory/`.
   - Update the relevant workstream, `todo.md`, and `session-log.md` after meaningful progress.
   - Promote durable delivery decisions when the source path, route status, or asset strategy becomes binding.
   - Record phase summaries, review status, backlog additions, manual-required gaps, and milestone stop state.
   - Generate a handoff when the work pauses midstream or another session must resume delivery.

## Reference Routing

- `references/intake-brief.md`: read when the user starts with a vague idea or incomplete product/site definition.
- `references/concept-generation.md`: read when visual direction or route mockups need to be generated.
- `references/historical-mock-pass.md`: read when repo-owned historical visuals or archived mockups should drive the current pass.
- `references/visual-provenance.md`: read before any image becomes authoritative.
- `references/design-system-docs.md`: read before creating or updating design docs.
- `references/design-fidelity-loop.md`: read when a design screenshot, mockup, generated route image, Figma export, or historical image should be matched closely in the final page.
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
- the current website milestone contract is visible and scoped to P0/P1 work
- from-zero or visually open work has either a user-selected visual direction recorded or is explicitly limited to `Framework Ready`
- the pre-code document gate exists: intake output, design docs, and implementation map
- the visual source map identifies image origins and authority
- design-system and route docs exist or have been updated
- core routes are implemented responsively
- any framework-first milestone is explicitly labeled as such
- temporary-binding route owners and upgrade triggers are documented when provisional imagery remains
- local or owned assets are used where possible
- build/typecheck passes
- desktop and mobile browser QA have been run
- binding design references have reference decomposition, implementation screenshot, side-by-side comparison, deviation backlog, and a final fidelity status
- every binding route has a page-by-page, item-by-item fidelity audit with no unchecked required items or unresolved blocking item mismatches
- generated UI asset prompts and resulting assets are recorded when generation is needed to match the design
- production readiness has been reviewed
- known gaps are explicitly reported
