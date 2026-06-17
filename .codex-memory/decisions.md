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
