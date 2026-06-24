# Decisions
## 2026-06-24 - Split Image Assets Applies Concept-C Field Retrospective
- Decision: Treat professional segmentation/matting as the required primary production extraction path, while keeping Pillow/OpenCV/skimage as helper tools only. Enforce source-space masks at import time, standardize `_staging/` and `_archive_intermediate/`, reject loose root-level intermediate outputs, and require `reconstruction_provenance` plus manual confirmation for approximate/reconstructed layers before `qa.status=pass`.
- Rationale: The `concept-c-workshop-console.png` trial showed the skill's package and QA contract worked, but practical runs could still drift into coordinate crops, tight bbox masks, loose SAM output folders, and background plates described as extraction rather than reconstruction.
- Impact: `init_asset_package.py` now creates intermediate directories; `import_external_assets.py` rejects tight bbox masks when a source-space mask is required; `validate_asset_package.py` detects unarchived intermediates and approximate reconstruction without provenance. Docs now guide high-signal subset extraction and UI tile/glyph decomposition.
- Related files: `split-image-assets/scripts/init_asset_package.py`, `split-image-assets/scripts/import_external_assets.py`, `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/references/pipeline-recipes.md`, `split-image-assets/references/qa-standards.md`, `docs/usage/split-image-assets.md`

## 2026-06-24 - Split Image Assets Requires Pre-Extraction Capability And Granularity Gates
- Decision: Add a deterministic extraction environment check and make granularity alignment a required pre-extraction workflow gate. Also block `qa.status=pass` for bbox/manual-estimated crop layers unless `manual_review_confirmed=true` is recorded per layer.
- Rationale: The package contract and validator were strong, but user testing showed agents could still start a run without knowing whether mature extraction tools were available or what split granularity the user needed. Crop-only outputs could also be mistaken for production assets without an explicit human acceptance record.
- Impact: `scripts/check_extraction_environment.py` reports local optional tool availability without installing anything. `SKILL.md`, workflow, recipes, usage docs, and validation now require capability checks, granularity alignment, and explicit crop-only confirmation before production-pass claims.
- Related files: `split-image-assets/scripts/check_extraction_environment.py`, `split-image-assets/scripts/record_quality_review.py`, `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/pipeline-recipes.md`, `split-image-assets/tests/test_skill_package.py`

## 2026-06-24 - Split Image Assets Requires Preview Evidence For Validation
- Decision: Make `validate_asset_package.py` require ordinary inspection previews and segmentation-quality previews for every reusable object layer before a package can validate structurally.
- Rationale: Manual testing showed a package could contain object PNGs, masks, and metadata but still lack the preview evidence needed to inspect segmentation and alpha quality. A package without preview evidence should not look ready merely because metadata does not reference missing previews.
- Impact: Validation now fails until `build_previews.py` creates white-background, checkerboard, overview, and sprite-sheet previews, and `build_quality_previews.py` creates mask overlay and alpha inspection previews. This keeps the mature-pipeline contract tied to visible QA evidence.
- Related files: `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/tests/test_skill_package.py`, `split-image-assets/SKILL.md`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/references/qa-standards.md`, `docs/usage/split-image-assets.md`

## 2026-06-24 - Split Image Assets Uses A Review Adapter Instead Of Hand-Edited QA Metadata
- Decision: Add `scripts/record_quality_review.py` as the supported path for recording semantic analysis, quality gates, object quality checks, package QA status, and `qa_report.md` notes after inspecting imported image layers.
- Rationale: Manual testing exposed a usability gap: external assets could be imported, but testers then had to hand-edit `metadata.json` to clear `needs-review` states and align `qa_report.md`. That made validation failures easy to create and hard to interpret.
- Impact: The skill now has a deterministic review step between quality previews and validation. The adapter refuses `qa.status=pass` unless every required object quality check is `pass`, preserving the existing quality gate while making the happy path testable.
- Related files: `split-image-assets/scripts/record_quality_review.py`, `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/asset-package-contract.md`, `docs/usage/split-image-assets.md`, `split-image-assets/tests/test_skill_package.py`

## 2026-06-23 - Split Image Assets Requires User Sync For Ambiguous Split Decisions
- Decision: Add a Decision Sync Rule to `split-image-assets`: when layer grouping, text ownership, background repair, animation readiness, or low-confidence mask handling requires product judgment, ask the user one focused question at a time and include a recommended answer before continuing that branch.
- Rationale: Mature segmentation tools can produce plausible pixels, but reusable assets depend on intent. Some split choices cannot be inferred safely from the image alone and should be resolved with the user instead of guessed.
- Impact: Future use of the skill should pause before ambiguous extraction choices while still allowing the agent to decide directly when evidence from the image, metadata, or user requirements is sufficient.
- Related files: `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/tests/test_skill_package.py`

## 2026-06-23 - Split Image Assets Uses Adapters Instead Of Vendored Models
- Decision: Add deterministic adapter and QA preview scripts to `split-image-assets` instead of vendoring SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, or model weights.
- Rationale: Mature image tools are heavy, fast-moving, and license/runtime-dependent. The stable product boundary is to normalize their outputs into a package contract, record provenance, generate review previews, and validate quality evidence.
- Impact: `import_external_assets.py` copies external outputs into package-owned paths and records tool/object metadata. `build_quality_previews.py` creates mask overlay and alpha inspection evidence. The skill can now reuse professional upstream tools while keeping repository scripts deterministic and lightweight.
- Related files: `split-image-assets/scripts/import_external_assets.py`, `split-image-assets/scripts/build_quality_previews.py`, `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/references/qa-standards.md`, `docs/usage/split-image-assets.md`

## 2026-06-23 - Split Image Assets Uses Pipeline Quality Gates
- Decision: Refactor `split-image-assets` around a quality-gated extraction pipeline contract inspired by Grounded-SAM/SAM2 segmentation, matting/refinement tools, background repair workflows, and Qwen-Image-Layered style RGBA layer decomposition.
- Rationale: External research showed that the most reliable real-world path is not one deterministic script, but a staged pipeline that records detection, segmentation, alpha refinement, background repair, layer packaging, and QA evidence. The skill should therefore validate provenance and quality evidence instead of pretending to judge visual segmentation automatically.
- Impact: Valid packages must now record `metadata.extraction_pipeline`, ordered stages, upstream tools, quality gates, and per-object `layer_kind`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`. A new `pipeline-recipes.md` reference documents recommended recipes while keeping external models optional.
- Related files: `split-image-assets/SKILL.md`, `split-image-assets/references/pipeline-recipes.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/references/qa-standards.md`, `split-image-assets/references/manual-review.md`, `split-image-assets/scripts/init_asset_package.py`, `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/tests/test_skill_package.py`, `docs/usage/split-image-assets.md`

## 2026-06-23 - Split Image Assets Requires Semantic Hierarchy Evidence
- Decision: Harden `split-image-assets` so valid packages must record `metadata.analysis.visual_hierarchy` and `metadata.analysis.recommended_split_plan`, and update the skill workflow to forbid rectangular crops or grid slices as substitutes for semantic layers.
- Rationale: A real test on the Project Atlas concept image showed that structurally valid crops can still be unusable when the agent does not understand the image hierarchy, background/backplate, core objects, route layers, labels, and decorations.
- Impact: Future packages must document the layer stack before validation can pass. The docs now emphasize semantic layers before rectangles, honest reconstructed backgrounds, manual-review flags for uncertain mattes, and `needs-review`/`blocked` when the result is mostly crops.
- Related files: `split-image-assets/SKILL.md`, `split-image-assets/references/workflow.md`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/references/qa-standards.md`, `split-image-assets/references/manual-review.md`, `split-image-assets/scripts/init_asset_package.py`, `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/tests/test_skill_package.py`, `docs/usage/split-image-assets.md`

## 2026-06-23 - Split Image Assets Separates Packaging From Segmentation
- Decision: Add `split-image-assets` as the sixth public repository skill and keep deterministic scripts scoped to asset-package initialization, preview generation, and validation rather than claiming to perform segmentation, matting, inpainting, or object recognition.
- Rationale: The user wanted a semi-automatic image-processing skill, but production-grade asset splitting depends on external AI/manual/image-editing steps for hard visual judgment. Keeping the script boundary explicit prevents false automation claims while still making the final asset package reusable, inspectable, and QA-backed.
- Impact: The new package ships `SKILL.md`, workflow/package/QA/manual-review references, three Python scripts, package tests, and repository navigation updates. Future work can add integrations with segmentation tools without weakening the current metadata and QA contract.
- Related files: `split-image-assets/SKILL.md`, `split-image-assets/scripts/init_asset_package.py`, `split-image-assets/scripts/build_previews.py`, `split-image-assets/scripts/validate_asset_package.py`, `split-image-assets/references/asset-package-contract.md`, `split-image-assets/tests/test_skill_package.py`, `docs/usage/split-image-assets.md`
## 2026-06-20 - Visual Resources Must Be Split By Maintainable Boundaries
- Decision: Treat `zero-to-website-design` visual resources as atomic file units before generation, sourcing, drawing, extraction, or local asset creation. Binding-route assets now require a Resource-To-File Map that records resource unit, unit type, output path, owner component, reuse scope, split reason, stay-separate rules, text policy, edit boundary, and status.
- Rationale: The V28 asset pipeline connected assets to route authority and evidence, but it still allowed a future agent to bake multiple independent resources into one raster because they appeared near each other in a reference image. Real usage showed that this creates brittle, hard-to-maintain pages.
- Impact: `zero-to-website-design` now blocks over-composited assets as `blocked-maintainability`, allows composites only with explicit rationale and child-resource boundaries, and requires templates plus QA reports to capture resource atomicity before `Visual Delivery Ready`.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/resource-atomicity.md`, `zero-to-website-design/references/visual-asset-pipeline.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/implementation-map.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/asset-and-data-spec.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-20 - Visual Assets Need A Pipeline Contract
- Decision: Treat generated, sourced, drawn, and local visual assets in `zero-to-website-design` as a pipeline contract that ties visual authority, reference region, implementation owner, asset slot or DOM component, evidence screenshot, difference status, and delivery claim together.
- Rationale: V27 closed many checklist gaps, but a future agent could still obey isolated rules while losing the asset graph: who owns each reference region, whether text belongs in DOM or imagery, whether tilt is CSS or baked, and whether the final claim exceeds the weakest visual asset status.
- Impact: `zero-to-website-design` now has a dedicated visual asset pipeline reference, template fields for owner/text/perspective/evidence status, delivery rules for weakest-asset claims, and mojibake regression coverage. Mojibake is treated as a visual delivery blocker, not just a cosmetic docs issue.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/visual-asset-pipeline.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/production-delivery.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-20 - Visual Delivery Needs Concrete Closure Evidence
- Decision: Require visually driven website work to capture user-selected concrete visual authority, Reference-To-DOM Maps, component-slot asset records, top 3 visible differences after each visual pass, visual usability gates, user-feedback status changes, and final visual pass reports before `Visual Delivery Ready`.
- Rationale: Real usage showed that even strong design rounds and fidelity language can still let agents implement from memory, skip concrete image selection, use generic placeholders, ignore obvious screenshot differences, or overclaim delivery after build/QA passes.
- Impact: `zero-to-website-design` now makes visual delivery closure evidence part of the main workflow, references, templates, usage docs, and regression tests.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/production-delivery.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-20 - Website Design Must Progress Through Explicit Rounds
- Decision: Require `zero-to-website-design` to treat website design as explicit rounds inside the current milestone: context, visual direction selection, design-system decomposition, implementation map, implementation slice, fidelity fix loop, and final delivery gate.
- Rationale: The 13-gate workflow was too easy to treat as a single checklist. Real usage showed agents can skip visual selection, start coding before design artifacts, or defer fidelity checks until the end.
- Impact: `zero-to-website-design` now routes the round contract through `references/design-rounds.md`, blocks broad implementation before Round 3 exits, and blocks final delivery when required rounds are skipped, unrecorded, or collapsed.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/design-rounds.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - Binding References Must Be Rebuilt As Interactive UI
- Decision: Forbid satisfying a binding design reference by shipping the whole reference screenshot as the page with transparent hotspots or invisible links.
- Rationale: A full-page image can look visually identical while failing the real website requirements: accessible text, maintainable DOM, responsive behavior, stateful controls, real links, and component reuse.
- Impact: `zero-to-website-design` now requires selected images to be decomposed into real DOM, components, local assets, controls, charts or diagrams, links, and responsive behavior. Full-page screenshot implementations block `Visual Delivery Ready`.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/route-acceptance.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - Design Audit Rows Need Verifiable Evidence
- Decision: Require every binding-route fidelity audit row to include verifiable evidence: screenshot paths, viewport, reference region/crop/coordinate/annotation, implementation region/crop/coordinate/annotation, evidence quality, and fresh recheck evidence after fixes.
- Rationale: Itemized audit tables can still become performative if rows only say "looks close" or "see screenshot." Another agent must be able to independently inspect the cited visual evidence.
- Impact: `zero-to-website-design` now treats `weak` evidence quality as insufficient for `Visual Delivery Ready` and requires fixed rows to point to updated implementation evidence.
- Related files: `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - Binding Design Matches Require Page Item Fidelity Audits
- Decision: Require page-by-page, item-by-item fidelity audits for every binding route and required viewport before `Visual Delivery Ready` or design-match claims.
- Rationale: A selected design image can still be implemented loosely if the agent only performs a high-level screenshot comparison. Real failures show the workflow must force comparison of hero, navigation, sections, repeated components, typography, asset slots, decorative resources, spacing, and responsive states one by one.
- Impact: `zero-to-website-design` now treats unchecked design items and blocked item-level mismatches as blockers. The QA report template and route evidence contract include an itemized audit path/table.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/route-acceptance.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - User-Selected Visual Direction Is A Hard Gate For From-Zero Sites
- Decision: Treat user selection from visible visual directions, homepage mockups, or route mockups as a required pre-code gate for from-zero visually open website work unless the milestone is explicitly framework-only.
- Rationale: A real usage failure showed that an agent can treat text mood direction and a working engineering scaffold as enough authority, then skip the user's visual choice. That produces a runnable site but not a final visual design.
- Impact: `zero-to-website-design` now requires 2-4 candidate visual directions or mockups, user selection or explicit framework-only authorization, and clear `Framework Ready` labeling when final visual direction is still unapproved.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/concept-generation.md`, `zero-to-website-design/references/visual-provenance.md`, `zero-to-website-design/references/framework-first-delivery.md`, `zero-to-website-design/references/production-delivery.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - Palette-Only Restyling Is A Blocking Reference Fidelity Failure
- Decision: Treat "just recolored the page" implementations as blocking visual failures when a binding design reference exists.
- Rationale: A real usage failure showed that a page can reuse colors, rounded corners, or fonts while still missing the design image's actual layout geometry, component silhouettes, custom resources, hierarchy, and decorative systems. That behavior must not be accepted as a fidelity pass.
- Impact: `zero-to-website-design` now explicitly requires agents to redraw, code, or generate missing UI components and resources, then re-check with side-by-side screenshots before claiming the implementation follows the design.
- Related files: `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-19 - Make Design Screenshot Fidelity A First-Class Website Gate
- Decision: Add a dedicated design fidelity loop to `zero-to-website-design` and make it a required gate whenever a screenshot, mockup, generated route image, Figma export, or historical image controls the final page.
- Rationale: The previous workflow could pass build and screenshot QA while still producing a page that was only loosely similar to the reference. Binding design images need decomposition, asset prompt planning, implementation screenshots, side-by-side comparison evidence, and a fix loop before a visual readiness claim is credible.
- Impact: Future website work should document reference decomposition, fidelity budget, generated UI asset prompts, comparison evidence, deviation backlog, and final fidelity status before claiming `Visual Delivery Ready`.
- Related files: `zero-to-website-design/SKILL.md`, `zero-to-website-design/references/design-fidelity-loop.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/implementation-map.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`
## 2026-06-19 - Guard Destructive Skill Install Targets Before Clean Copy
- Decision: Keep the existing clean-copy install/update behavior for `production-code-quality-review`, but require both helper scripts to validate the resolved target before any `rm -rf`.
- Rationale: Clean-copy is useful for removing generated cache artifacts, yet environment-derived install paths and recorded source metadata are too risky to trust without guardrails. The smallest production-safe fix is to prove the target still looks like the intended skill install directory and is not equal to or nested with the source checkout.
- Impact: Installs and updates now reject empty, root-like, home/skill-root, source-equal, target-inside-source, and source-inside-target cases before deletion. Static regression coverage protects the contract in Windows environments where POSIX runtime helper tests are skipped.
- Related files: `production-code-quality-review/scripts/install-local-skill.sh`, `production-code-quality-review/scripts/update-local-skill.sh`, `production-code-quality-review/tests/test_collect_review_context_cli.py`, `docs/dev/2026-06-19-production-code-quality-review-v19-install-path-guard-plan.md`
## 2026-06-19 - Make Submitted Skills Milestone-Driven
- Decision: Align `best-project-memory`, `production-code-quality-review`, and `zero-to-website-design` around a finite milestone-driven production mode with frozen P0/P1 scope, backlog/manual-required routing, phase-gate reviews, atomic phase closure, and explicit stop conditions.
- Rationale: The EvoMap submission should demonstrate a reusable production execution loop, not just individual skill capabilities. The three skills cover complementary parts of that loop: memory and milestone control, phase-end production review, and bounded website delivery.
- Impact: Future project tasks that use these skills should define the current milestone, execute only P0/P1 work, review phase increments, record backlog/manual-required gaps, summarize, and stop instead of drifting into open-ended optimization.
- Related files: `docs/dev/2026-06-19-awesome-skills-v17-milestone-driven-production-mode-plan.md`, `best-project-memory/SKILL.md`, `production-code-quality-review/SKILL.md`, `zero-to-website-design/SKILL.md`
## 2026-06-18 - Close The Paused Repository Docs Line
- Decision: Do not resume another repository-level documentation phase without a concrete new gap.
- Rationale: The refreshed README, release-scope correction, skill matrix, docs regression tests, and zero-to-website usage alignment already close the known repository-level navigation and scope issues.
- Impact: The active TODO set can close cleanly. Future repository docs work should start from a new explicit trigger such as a new package, release surface, install path, or skill-selection ambiguity.
## 2026-06-18 - Public Usage Workflow Must Match The Skill Workflow
- Decision: Treat the public `zero-to-website-design` usage workflow summary as part of the package contract and align it to the 12-step `SKILL.md` workflow.
- Rationale: The skill body already requires project-memory integration as step 12, while the usage guide still described only eleven gates. This drift could cause users to miss long-running memory behavior even though the skill implements it as a completion expectation.
- Impact: The usage guide now describes 12 gates and regression tests protect the visible count plus project-memory integration step.
## 2026-06-18 - Commit Production Review Mainline Sync As A Standalone Phase
- Decision: Commit the pending `production-code-quality-review/` sync as V13 after proving the directory matches `origin/main`.
- Rationale: The dirty diff is not an accidental local edit; it aligns the package with GitHub mainline `f1eac46 Refine staged review modes`, passes the package tests, and validates as a skill. Keeping it uncommitted would keep unrelated review-package changes in every future working-tree review.
- Impact: The branch-local review-memory write path is removed from the active package in favor of the mainline staged-review-mode implementation, while historical docs keep the earlier experiment traceable.
## 2026-06-18 - Pre-Code Artifacts Must Gate Broad Website Implementation
- Decision: Use a pre-code document-gate hardening pass as the V11 stage for `zero-to-website-design`, and require a preserved intake output, design-doc baseline, and implementation map before broad implementation begins.
- Rationale: The V6-V10 workflow already makes provenance, QA evidence, and delivery state much stricter, but the intake-to-implementation handoff still left too much room for backfilling key planning artifacts after code had already started. Tightening the earlier gate reduces workflow drift where route scope, source-path choice, and milestone intent first become binding.
- Alternatives considered: Opening another later-stage QA or template pass first, or relying on users to infer the pre-code gate from scattered wording across the existing references.
- Impact: The package now makes route inventory, deferred routes, source-path choice, milestone target, prerequisite docs, and implementation-map blockers more explicit across the references, `SKILL.md`, usage docs, and regression coverage.
- Rollback trigger: If downstream projects show that the pre-code gate has become too heavy for small sites, keep the artifact chain requirement but trim low-value wording while preserving the intake, route-scope, and implementation-map checkpoints.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v11-precode-doc-gate-plan.md`, `zero-to-website-design/references/intake-brief.md`, `zero-to-website-design/references/design-system-docs.md`, `zero-to-website-design/references/implementation-map.md`, `zero-to-website-design/SKILL.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Release-Facing Docs Must Describe The Repository Scope, Not Only One Package
- Decision: Use a repository-level release-docs scope correction as V11 so public release-facing docs stop implying that only `production-code-quality-review` defines the repo's shipped documentation surface.
- Rationale: After V6-V10, the strongest remaining public-facing drift is in the repository navigation layer. The repo README already describes a three-skill collection, but the English and Chinese release indexes still describe themselves as if they belonged only to one package.
- Alternatives considered: Opening another `zero-to-website-design` contract-hardening pass first, or creating formal versioned release-note files for every skill immediately.
- Impact: Release-facing docs now explain that formal versioned release notes currently ship for `production-code-quality-review`, while `best-project-memory` and `zero-to-website-design` are routed through usage docs and staged development notes.
- Rollback trigger: If the repository later adds formal release-note files for the other packages, simplify this wording into a broader package matrix instead of keeping the "current scope" explanation.
- Related files: `docs/dev/2026-06-18-awesome-skills-v11-release-docs-scope-correction-plan.md`, `README.md`, `docs/releases/README.md`, `docs/zh/README.zh-CN.md`, `docs/zh/releases/README.zh-CN.md`, `tests/test_repository_docs.py`
## 2026-06-18 - Delivery Templates Must Carry The Stronger Workflow Contract
- Decision: Use template-contract hardening as the V10 stage for `zero-to-website-design`, and align the shipped implementation, page-spec, asset/data, and design-system templates with the stricter V6-V9 provenance and QA rules.
- Rationale: The reference docs now require route readiness state, route evidence, source ownership, replacement triggers, and handoff-sensitive gaps, but several copied scaffolds still under-recorded those fields. That mismatch would cause downstream repos to drift back to weaker delivery artifacts.
- Alternatives considered: Opening another reference-only prose pass, or adding brand-new templates instead of strengthening the existing ones.
- Impact: The package templates now make it natural to record route-owner risk, weakest route status, viewport evidence targets, source method, authority status, replacement triggers, and final route-readiness gates.
- Rollback trigger: If downstream projects show the new template fields are too heavy for small sites, trim low-value wording while keeping the route status, ownership, and replacement fields.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v10-template-contract-hardening-plan.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/page-spec.md`, `zero-to-website-design/assets/templates/asset-and-data-spec.md`, `zero-to-website-design/assets/templates/design-system-master.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-17 - Route QA Must Produce Evidence Before Readiness Claims
- Decision: Treat route acceptance and browser QA evidence as the V9 hardening target for `zero-to-website-design`.
- Rationale: V6-V8 made visual source authority stricter, but a production website pass can still overclaim readiness if route, viewport, screenshot, console, overflow, link, asset, and gap evidence are not recorded together.
- Alternatives considered: Adding another source-provenance pass, or adding browser automation scripts before tightening the written contract.
- Impact: The package now requires compact route evidence rows, explicit failure classification, and final readiness claims tied to the weakest required route status.
- Rollback trigger: If downstream projects find the evidence rows too heavy for small sites, keep the readiness rules but allow an even smaller route evidence format.
- Related files: `docs/dev/2026-06-17-zero-to-website-design-v9-qa-evidence-contract-plan.md`, `zero-to-website-design/references/route-acceptance.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/production-delivery.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Generated Concepts Need Explicit Authority Escalation Rules
- Decision: Treat generated-image escalation as its own hardening target immediately after provenance-contract hardening, so `concept-generation.md` no longer relies on implied judgment about when a generated mockup can become route-authoritative.
- Rationale: Once provenance artifacts are strict, the next likely source of workflow drift is not where authority is recorded but how generation enters the system and climbs the authority ladder. This is especially important for preventing unnecessary generation when repo-owned visuals were already sufficient.
- Alternatives considered: Leaving the generated-image path as-is, or postponing generation hardening until after another template-focused pass.
- Impact: The next `zero-to-website-design` stage should encode stricter generation-entry conditions, escalation rules, and replacement triggers for generated route owners.
- Rollback trigger: If downstream usage shows that the stricter generation rules add too much ceremony for genuine zero-to-one website work, reduce the wording burden while keeping the explicit route-owner and replacement checks.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v8-concept-authority-hardening-plan.md`, `zero-to-website-design/references/concept-generation.md`, `zero-to-website-design/SKILL.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Provenance Templates Must Match The Stronger Temporary-Binding Contract
- Decision: Treat `references/visual-provenance.md` and `assets/templates/visual-source-map.md` as part of the same hard requirement surface as the workflow text, and harden them immediately after V6.
- Rationale: V6 raised the bar for temporary-binding ownership, milestone support, and replacement tracking. Leaving the provenance artifacts on the older lighter schema would reintroduce doc drift exactly where projects record source-of-truth decisions.
- Alternatives considered: Waiting for a later general cleanup pass, or relying on users to infer the missing provenance fields from SKILL-level wording alone.
- Impact: The next `zero-to-website-design` stage should tighten provenance rows and authority guidance so the package's workflow and project artifacts stay aligned.
- Rollback trigger: If downstream projects show that the stricter provenance row becomes too heavy for ordinary site work, trim low-value fields while preserving ownership scope and replacement tracking.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v7-provenance-contract-hardening-plan.md`, `zero-to-website-design/references/visual-provenance.md`, `zero-to-website-design/assets/templates/visual-source-map.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Historical Repo Images Should Drive Framework-First Website Passes Before New Generation
- Decision: Treat repo-owned mockups, screenshots, and prior concept images as the preferred visual authority for a website's framework-ready pass when they are already strong enough to control route composition.
- Rationale: In real project work, users often want layout, route framing, and responsive structure delivered before bespoke imagery is ready. Forcing fresh image generation too early adds latency and can distract from the higher-value shell and interaction work.
- Alternatives considered: Keeping historical visuals as only a soft fallback, or making fresh image generation the default next move whenever the site still lacks final artwork.
- Impact: The next `zero-to-website-design` hardening pass should make "use local historical images first, do not generate new ones yet" a first-class documented workflow while keeping asset provenance and upgrade triggers explicit.
- Rollback trigger: If downstream projects show that this path causes too much ambiguity about what is acceptable for delivery, tighten the route-acceptance and temporary-binding rules rather than removing the path entirely.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v6-historical-mock-framework-hardening-plan.md`, `zero-to-website-design/references/historical-mock-pass.md`, `zero-to-website-design/references/framework-first-delivery.md`, `docs/usage/zero-to-website-design.md`
## 2026-06-17 - Start V2 Multi-skill Integration at Read-only Level
- Decision: Integrate `production-code-quality-review` with `best-project-memory` as a Level 1 read-only consumer first.
- Rationale: The review skill benefits immediately from project-state and workstream awareness, while read-only integration limits coupling and keeps the new contract easy to validate.
- Alternatives considered: Jumping straight to read+append or governance-aware orchestration.
- Impact: Review setup now surfaces repo memory context without mutating project memory; future stages can build on the new schema and tests.
- Rollback trigger: If memory loading makes review output noisy or unstable, remove the `project_memory` projection while keeping the underlying memory files intact.
- Related files: `production-code-quality-review/scripts/review_skill_lib.py`, `production-code-quality-review/references/review-context.schema.json`, `production-code-quality-review/tests/test_collect_review_context_cli.py`, `production-code-quality-review/tests/test_review_skill_lib.py`
## 2026-06-18 - Zero-To-Website Templates Must Carry Delivery-State Memory
- Decision: Treat the `zero-to-website-design` shipped templates as part of the memory contract, not just the references and `SKILL.md`.
- Rationale: V3 and V4 expanded the workflow to include provenance upgrades, framework-ready versus delivery-ready milestones, workstreams, and handoffs. Leaving the templates behind would cause downstream project docs to regress into an older contract even when the package instructions were newer.
- Alternatives considered: Keeping the new behavior documented only in references and asking users to improvise their own workstream/handoff structure.
- Impact: The package now ships memory-aware scaffolds for implementation plans, page specs, QA reports, visual source maps, and website workstreams, with regression tests protecting that contract.
- Rollback trigger: If downstream projects prove these fields too heavy for ordinary website work, trim the templates while preserving the provenance and milestone fields that the workflow depends on.
- Related files: `zero-to-website-design/assets/templates/visual-source-map.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/page-spec.md`, `zero-to-website-design/assets/templates/qa-report.md`, `zero-to-website-design/assets/templates/website-workstream.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Keep Session Compaction Conservative And Structure-Aware
- Decision: Make `compact_session.py` compact only well-formed structured session entries and preserve the newest entries verbatim.
- Rationale: Session history is human-summary dominant state. A conservative helper reduces reading cost without guessing through malformed legacy logs or overwriting the active continuation surface.
- Alternatives considered: Fully rewriting all historical entries into a new canonical format, or compacting every line regardless of structure quality.
- Impact: Long-running repos can shrink old `session-log.md` history into a deterministic summary and optional phase recap while keeping recent execution detail readable and trustworthy.
- Rollback trigger: If real repositories show that the structured-only parser leaves too much noisy history untouched, broaden the parser with additional accepted legacy formats and regression tests.
- Related files: `best-project-memory/scripts/compact_session.py`, `best-project-memory/tests/test_skill_package.py`, `docs/usage/best-project-memory.md`, `docs/dev/2026-06-18-best-project-memory-v6-session-compaction-plan.md`
## 2026-06-18 - Keep Memory Lint Conservative But More Drift-Aware
- Decision: Extend `memory_lint.py` with warning-level drift checks for session-log growth and latest-snapshot visibility, while making missing referenced snapshots hard failures.
- Rationale: Phase 4 needs stronger enforcement of the governance loop, but the package should still avoid auto-fixing or over-asserting semantics it cannot prove.
- Alternatives considered: Leave lint purely structural, or upgrade every drift signal to an error.
- Impact: The quality gate now catches obvious evidence drift earlier without becoming noisy enough to discourage use.
- Rollback trigger: If the new warnings prove too chatty in real repos, raise the thresholds before removing the checks entirely.
- Related files: `best-project-memory/scripts/memory_lint.py`, `best-project-memory/tests/test_skill_package.py`, `docs/usage/best-project-memory.md`, `docs/dev/2026-06-18-best-project-memory-v7-quality-drift-hardening-plan.md`
## 2026-06-18 - Keep Review Memory Writes Opt-In And Level 2 Scoped
- Decision: Add review continuity writes to `production-code-quality-review` only as an explicit opt-in path that appends a session block and merges follow-up TODO items, without promoting decisions or generating handoffs.
- Rationale: The V2 plan needs proof of a Level 2 read+append integration, but production review should remain safe and low-surprise by default.
- Alternatives considered: Keep the review skill fully read-only, or automatically write memory on every review invocation.
- Impact: The repository now proves both Level 1 and Level 2 integration patterns while preserving a conservative default review workflow.
- Rollback trigger: If the write path causes noisy or duplicate continuity updates in real review workflows, keep the helper but narrow the flags or extract the behavior into a separate wrapper command.
- Related files: `production-code-quality-review/scripts/review-entrypoint.py`, `production-code-quality-review/scripts/review_skill_lib.py`, `production-code-quality-review/tests/test_collect_review_context_cli.py`, `production-code-quality-review/tests/test_review_skill_lib.py`, `docs/dev/2026-06-18-production-code-quality-review-v8-level2-memory-integration-plan.md`
## 2026-06-18 - Route Explicitly Urgent Review Follow-Ups Into In-Progress Work
- Decision: Treat only explicitly marked `P1:`, `Blocker:`, and `Urgent:` review follow-ups as `## In Progress` TODO items, and dedupe normalized follow-ups across both active TODO sections.
- Rationale: V9 needs better continuity signal than the all-to-`Next` V8 behavior, but should still avoid fuzzy prioritization or silent workstream rewrites.
- Alternatives considered: Keep routing all items to `## Next`, or add broader fuzzy matching and automatic reprioritization.
- Impact: Repeated review cycles can record urgent actions without burying them in backlog noise, while exact normalized duplicates stop accumulating across active TODO sections.
- Rollback trigger: If explicit marker routing proves too rigid in real review flows, broaden the accepted markers before adding heavier priority inference.
- Related files: `production-code-quality-review/scripts/review_skill_lib.py`, `production-code-quality-review/tests/test_review_skill_lib.py`, `production-code-quality-review/tests/test_collect_review_context_cli.py`, `docs/dev/2026-06-18-production-code-quality-review-v9-followup-routing-plan.md`
## 2026-06-18 - Sync Public Docs Before Choosing The Next Code-Heavy V2 Target
- Decision: Use a documentation-sync pass as V10 before opening the next code-heavy V2 integration stage.
- Rationale: The repository has already shipped meaningful V5-V9 continuity behavior, but the main governance plan and release-facing docs still lag behind filesystem truth. Choosing the next engineering target from stale docs would weaken traceability.
- Alternatives considered: Jump directly into another code integration stage and defer doc sync until a later release.
- Impact: The next target selection will be grounded in a current, auditable summary of the proven Level 1, Level 2, and Level 3 continuity surface.
- Rollback trigger: If the repo later adopts a separate release-management flow that already mirrors these staged outcomes, keep only the main V2 plan sync and trim the broader doc updates.
- Related files: `docs/dev/2026-06-17-best-project-memory-v2-governance-plan.md`, `docs/dev/2026-06-18-best-project-memory-v10-doc-sync-plan.md`, `docs/usage/best-project-memory.md`, `README.md`, `.codex-memory/project-state.md`, `.codex-memory/todo.md`
## 2026-06-18 - Harden Repair Before Expanding The Remaining V2 Surface
- Decision: Use `init_memory.py --repair` as the next code stage and make it explicitly restore partial memory layouts without overwriting existing files.
- Rationale: The V2 plan names repair as part of the helper surface, but the current implementation is only minimally proven. Repair is the clearest remaining code-backed gap after V10 documentation sync.
- Alternatives considered: Start another broader integration phase first, or leave repair behavior as-is and only document it.
- Impact: `best-project-memory` now gets a deterministic recovery path for incomplete `.codex-memory/` layouts, with a regression that proves existing files are preserved.
- Rollback trigger: If repair later needs to support more corrupted layouts, extend the helper carefully rather than broadening overwrite behavior.
- Related files: `best-project-memory/scripts/init_memory.py`, `best-project-memory/tests/test_skill_package.py`, `docs/dev/2026-06-18-best-project-memory-v11-repair-hardening-plan.md`, `docs/usage/best-project-memory.md`
## 2026-06-18 - Harden Stale TODO Detection With Conservative Evidence Rules
- Decision: Upgrade `stale_todo_check.py` to flag active TODO items that already appear in `## Done`, and strengthen that warning when recent `session-log.md` `Next:` evidence points at the same normalized item.
- Rationale: The V2 plan promises stale/dirty-state detection, but the previous script only checked vague wording. Active-versus-done duplication is a deterministic, low-noise signal that fits the package's conservative quality-gate style.
- Alternatives considered: Keep the script as a wording-only checker, or jump straight to fuzzy semantic completion inference.
- Impact: The stale TODO gate now catches a more meaningful class of dirty active state without needing brittle natural-language interpretation.
- Rollback trigger: If real repositories show too many false positives from exact normalized duplication, narrow the duplicate rule before adding any broader inference.
- Related files: `best-project-memory/scripts/stale_todo_check.py`, `best-project-memory/tests/test_skill_package.py`, `docs/dev/2026-06-18-best-project-memory-v12-stale-todo-hardening-plan.md`, `docs/usage/best-project-memory.md`
## 2026-06-18 - Close V2 As Delivered And Use Future Work As Post-V2 Enhancements
- Decision: Treat the current repository state as the completed `best-project-memory` V2 delivery baseline.
- Rationale: The planned governance helpers, quality controls, multi-skill integration proofs, release-facing documentation sync, and regression coverage are all present and validated in the current repository state.
- Alternatives considered: Open another narrow hardening stage before closure, or leave the completion judgment implicit without a delivery summary.
- Impact: Future improvements can be scoped as post-V2 enhancements rather than as unresolved obligations inside the original V2 plan.
- Rollback trigger: If a missing V2 requirement is later discovered with concrete repository evidence, reopen a bounded follow-up stage against that specific requirement.
- Related files: `docs/dev/2026-06-17-best-project-memory-v2-governance-plan.md`, `.codex-memory/phases/2026-06-18-v2-delivery-summary.md`, `.codex-memory/project-state.md`, `.codex-memory/todo.md`
## 2026-06-18 - Make The Repository Introduction Explicitly Multi-Skill
- Decision: Refresh the top-level English and Chinese introduction docs around the repository as a three-skill catalog instead of centering them on only one package.
- Rationale: The repository has grown into a multi-skill collection, but the most visible intro pages still made the scope feel narrower than the actual shipped surface. A landing reader should understand the full inventory within a few seconds.
- Alternatives considered: Leave the root README mostly as-is and rely on deeper usage docs, or add a new overview doc without changing the main entry pages.
- Impact: The main introduction now explains which skills the repository contains, what each one is for, and where readers should go next in both languages.
- Rollback trigger: If the repository later splits into separate packages or a generated docs site becomes the primary entrypoint, simplify the README back to a thinner navigation layer.
- Related files: `README.md`, `docs/zh/README.zh-CN.md`, `docs/dev/2026-06-18-awesome-skills-overview-doc-refresh-plan.md`
## 2026-06-18 - Sync Production Review Skill To GitHub Latest
- Decision: Treat `origin/main` as the source of truth for `production-code-quality-review` and update the local skill directory from that snapshot.
- Rationale: The remote `main` branch contains newer skill changes than the local checkout, and the package should be kept aligned with the shipped GitHub version before any further edits.
- Impact: The local working tree now reflects the latest published skill package contents, including the updated staged review-mode `SKILL.md`.
## 2026-06-18 - Repository Skill Selection Should Have Its Own Matrix Page
- Decision: Add a top-level `docs/usage/skill-matrix.md` page as the primary repository-level chooser for the shipped skills.
- Rationale: The repo README and package docs already describe the individual skills, but a new reader still lacks one compact comparison page that answers "which skill should I use first?" quickly.
- Impact: The repository now has a reusable skill-selection surface that points users toward `best-project-memory`, `production-code-quality-review`, or `zero-to-website-design` without forcing them to infer the differences from package-specific docs.
## 2026-06-19 - Public Navigation Must Treat Little Lighthouse Publisher As A First-Class Skill
- Decision: Update repository-level public docs after merging `little-lighthouse-blog-publisher` so the repo is consistently presented as a four-skill catalog.
- Rationale: The package exists on `main`, but release indexes, Chinese overview text, verification commands, and regression tests still carried older three-skill assumptions.
- Impact: Readers can now discover the blog publisher from the same README, matrix, release-index, Chinese overview, and verification surfaces as the other shipped skills.
