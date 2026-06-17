# Project State

## Objective
- Keep the shipped skills in `awesome-skills` aligned with GitHub mainline while preserving the published `zero-to-website-design` website-generation workflow and repository navigation docs.

## Current Phase
- Current stage: V13 `production-code-quality-review` mainline sync is implemented in the working tree after proving the package matches `origin/main`.

## Current Branch
- `codex/best-project-memory-expansion`

## Last Verified
- 2026-06-18: `git diff --stat origin/main -- production-code-quality-review` reported no package differences.
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- 2026-06-18: `git push origin codex/best-project-memory-expansion` succeeded through `ad8e227`.
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-18: `$env:PYTHONUTF8='1'; python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-17: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-17: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-17: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-17: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-17: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-17: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-17: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- 2026-06-18: `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Active Risks
- The V13 sync intentionally removes the branch-local review-memory write path from `production-code-quality-review`; keep historical memory-integration docs as the record of that experiment.

## Active Blockers
- None for the website-generation skill publication path.

## Current Focus
- Commit and push the standalone V13 `production-code-quality-review` mainline sync, then return to the next bounded `zero-to-website-design` hardening choice.

## Next Milestone
- Commit and push V13, then select and document the next `zero-to-website-design` hardening stage.

## Key Artifacts
- `best-project-memory/SKILL.md`
- `docs/dev/2026-06-17-best-project-memory-v2-governance-plan.md`
- `docs/dev/2026-06-18-best-project-memory-v6-session-compaction-plan.md`
- `docs/dev/2026-06-18-best-project-memory-v7-quality-drift-hardening-plan.md`
- `docs/dev/2026-06-18-production-code-quality-review-v8-level2-memory-integration-plan.md`
- `docs/dev/2026-06-18-production-code-quality-review-v9-followup-routing-plan.md`
- `docs/dev/2026-06-18-best-project-memory-v10-doc-sync-plan.md`
- `docs/dev/2026-06-18-best-project-memory-v11-repair-hardening-plan.md`
- `docs/dev/2026-06-18-best-project-memory-v12-stale-todo-hardening-plan.md`
- `docs/dev/2026-06-18-awesome-skills-overview-doc-refresh-plan.md`
- `.codex-memory/phases/2026-06-18-v2-integration-summary.md`
- `.codex-memory/phases/2026-06-18-v2-delivery-summary.md`
- `docs/dev/2026-06-17-zero-to-website-design-v3-implementation-plan.md`
- `docs/dev/2026-06-17-zero-to-website-design-v4-memory-integration-plan.md`
- `docs/dev/2026-06-17-zero-to-website-design-v5-memory-aware-templates-plan.md`
- `docs/dev/2026-06-18-zero-to-website-design-v6-historical-mock-framework-hardening-plan.md`
- `docs/dev/2026-06-18-zero-to-website-design-v7-provenance-contract-hardening-plan.md`
- `docs/dev/2026-06-18-zero-to-website-design-v8-concept-authority-hardening-plan.md`
- `docs/dev/2026-06-17-zero-to-website-design-v9-qa-evidence-contract-plan.md`
- `docs/dev/2026-06-18-zero-to-website-design-v10-template-contract-hardening-plan.md`
- `docs/dev/2026-06-18-zero-to-website-design-v11-precode-doc-gate-plan.md`
- `docs/dev/2026-06-18-awesome-skills-v11-release-docs-scope-correction-plan.md`
- `docs/dev/2026-06-18-awesome-skills-v12-skill-matrix-plan.md`
- `docs/dev/2026-06-18-production-code-quality-review-v13-mainline-sync-plan.md`
- `best-project-memory/scripts/compact_session.py`
- `best-project-memory/scripts/memory_lint.py`
- `production-code-quality-review/scripts/review-entrypoint.py`
- `production-code-quality-review/scripts/review_skill_lib.py`
- `README.md`
- `docs/zh/README.zh-CN.md`
- `zero-to-website-design/SKILL.md`
- `zero-to-website-design/references/concept-generation.md`
- `zero-to-website-design/references/visual-provenance.md`
- `zero-to-website-design/references/historical-mock-pass.md`
- `zero-to-website-design/references/framework-first-delivery.md`
- `zero-to-website-design/references/project-memory-integration.md`
