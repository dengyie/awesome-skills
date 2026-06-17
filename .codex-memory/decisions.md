# Decisions
## 2026-06-18 - Metadata, Route-Data, And Feed Outputs Need A Single Integrity Contract
- Decision: Use metadata-route-data-feed integrity hardening as the V14 stage for `zero-to-website-design`, and bind route-data source of truth, metadata source of truth, and feed/export source of truth into the route acceptance and delivery contract.
- Rationale: V13 closed the content-source gap, but route generation and exported outputs can still drift independently from rendered pages. A dedicated integrity contract reduces the chance that a site looks correct while its slugs, metadata, or feed outputs disagree.
- Alternatives considered: Leave the output-parity checks distributed across existing references, or add runtime checks before the package-level wording was tightened.
- Impact: The package now makes route-data, metadata, and feed parity visible in implementation planning, route acceptance, QA reporting, and final delivery.
- Rollback trigger: If small static projects find the new wording too heavy, keep route-data ownership and parity checks while trimming feed-specific language where outputs do not exist.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v14-metadata-route-data-feed-integrity-plan.md`, `zero-to-website-design/references/implementation-map.md`, `zero-to-website-design/references/route-acceptance.md`, `zero-to-website-design/references/visual-qa-checklist.md`, `zero-to-website-design/references/production-delivery.md`, `zero-to-website-design/assets/templates/implementation-plan.md`, `zero-to-website-design/assets/templates/qa-report.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Content And Data Source Readiness Must Limit Delivery Claims
- Decision: Use content-and-data readiness hardening as the V13 stage for `zero-to-website-design`, and add a dedicated content-readiness reference plus aligned template and delivery wording.
- Rationale: The workflow already made visual sources, QA evidence, pre-code docs, and continuity explicit, but content/data readiness remained distributed across several lighter references. A dedicated contract reduces drift around placeholder policy, route-family ownership, metadata integrity, and when framework-first content can still support a valid milestone.
- Alternatives considered: Leave content readiness as scattered wording, or fold the new rules into an existing reference without creating a dedicated entry point.
- Impact: The package now names content source classes, route-family ownership, placeholder and generated-draft triggers, and the blockers that limit final delivery claims.
- Rollback trigger: If downstream projects show the new contract is too heavy for small static sites, trim low-value wording while preserving route-family ownership, content-source status, and blocker visibility.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v13-content-readiness-contract-plan.md`, `zero-to-website-design/references/content-readiness.md`, `zero-to-website-design/references/design-system-docs.md`, `zero-to-website-design/references/framework-first-delivery.md`, `zero-to-website-design/references/production-delivery.md`, `zero-to-website-design/assets/templates/asset-and-data-spec.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Workstream And Handoff Artifacts Must Preserve Resume-Critical State
- Decision: Use workstream-and-handoff continuity hardening as the V12 stage for `zero-to-website-design`, and require route matrix slices, weakest-route evidence, blocker ownership, and explicit handoff cues in the shipped continuity artifacts.
- Rationale: The V11 gate protects the start of implementation, but long-running website work still risks losing the restart context once a session pauses. Encoding the resume-critical state in filesystem artifacts reduces chat dependence without expanding the contract beyond what a resumed session actually needs.
- Alternatives considered: Leave continuity as an implied best practice, or add broader orchestration behavior before the artifact contract was proven.
- Impact: The package now makes workstream and QA scaffolds carry the next-session starting point, and tests lock the new wording in place.
- Rollback trigger: If the continuity fields prove too heavy for small sites, trim nonessential wording while preserving route slice, blocker owner, and handoff artifact requirements.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v12-workstream-handoff-hardening-plan.md`, `zero-to-website-design/references/project-memory-integration.md`, `zero-to-website-design/assets/templates/website-workstream.md`, `zero-to-website-design/assets/templates/qa-report.md`, `zero-to-website-design/SKILL.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
## 2026-06-18 - Pre-Code Artifacts Must Gate Broad Website Implementation
- Decision: Use a pre-code document-gate hardening pass as the V11 stage for `zero-to-website-design`, and require a preserved intake output, design-doc baseline, and implementation map before broad implementation begins.
- Rationale: The V6-V10 workflow already makes provenance, QA evidence, and delivery state much stricter, but the intake-to-implementation handoff still left too much room for backfilling key planning artifacts after code had already started. Tightening the earlier gate reduces workflow drift where route scope, source-path choice, and milestone intent first become binding.
- Alternatives considered: Opening another later-stage QA or template pass first, or relying on users to infer the pre-code gate from scattered wording across the existing references.
- Impact: The package now makes route inventory, deferred routes, source-path choice, milestone target, prerequisite docs, and implementation-map blockers more explicit across the references, `SKILL.md`, usage docs, and regression coverage.
- Rollback trigger: If downstream projects show that the pre-code gate has become too heavy for small sites, keep the artifact chain requirement but trim low-value wording while preserving the intake, route-scope, and implementation-map checkpoints.
- Related files: `docs/dev/2026-06-18-zero-to-website-design-v11-precode-doc-gate-plan.md`, `zero-to-website-design/references/intake-brief.md`, `zero-to-website-design/references/design-system-docs.md`, `zero-to-website-design/references/implementation-map.md`, `zero-to-website-design/SKILL.md`, `docs/usage/zero-to-website-design.md`, `zero-to-website-design/tests/test_skill_package.py`
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
