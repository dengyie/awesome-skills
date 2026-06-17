# Decisions
## 2026-06-17 - Start V2 Multi-skill Integration at Read-only Level
- Decision: Integrate `production-code-quality-review` with `best-project-memory` as a Level 1 read-only consumer first.
- Rationale: The review skill benefits immediately from project-state and workstream awareness, while read-only integration limits coupling and keeps the new contract easy to validate.
- Alternatives considered: Jumping straight to read+append or governance-aware orchestration.
- Impact: Review setup now surfaces repo memory context without mutating project memory; future stages can build on the new schema and tests.
- Rollback trigger: If memory loading makes review output noisy or unstable, remove the `project_memory` projection while keeping the underlying memory files intact.
- Related files: `production-code-quality-review/scripts/review_skill_lib.py`, `production-code-quality-review/references/review-context.schema.json`, `production-code-quality-review/tests/test_collect_review_context_cli.py`, `production-code-quality-review/tests/test_review_skill_lib.py`
