# Decisions
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
