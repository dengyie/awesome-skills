# Project State

## Objective
- Keep the shipped `awesome-skills` website-generation and repository-navigation workstreams complete, published, and traceable.

## Current Phase
- Current stage: V19 production-review install path guard is implemented and verified on `main`.

## Current Branch
- `main`

## Last Verified
- 2026-06-19: `$env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest production-code-quality-review.tests.test_collect_review_context_cli.CollectReviewContextCliTests.test_install_helpers_guard_destructive_target_cleanup -v`
- 2026-06-19: `$env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover production-code-quality-review\tests -v`
- 2026-06-19: `git diff --check`
- 2026-06-19: `$env:PYTHONUTF8='1'; python production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-19: `python production-code-quality-review\tests\test_review_skill_lib.py -v`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-19: `$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- 2026-06-19: `git diff --check`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- 2026-06-19: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\best-project-memory`
- 2026-06-19: `$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\production-code-quality-review`
- 2026-06-19: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-19: `$env:PYTHONUTF8='1'; python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
- 2026-06-19: `git diff --check`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- 2026-06-19: `python -m unittest discover E:\project\blog\awesome-skills\little-lighthouse-blog-publisher\tests -v`
- 2026-06-19: `git diff --check`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- 2026-06-18: `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- 2026-06-18: `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- 2026-06-18: `$env:PYTHONUTF8='1'; python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`
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
- POSIX runtime install/update negative-case tests could not run in this Windows environment because `bash` resolves to the WSL shim and WSL virtualization is unavailable. Static guard-contract tests and package tests pass.

## Active Blockers
- None for the V19 production-review install path guard.

## Current Focus
- Commit and push the V19 production-review install path guard on `main`.

## Next Milestone
- No next milestone is scheduled; start a new documented phase only when a concrete new gap appears.

## Key Artifacts
- `docs/dev/2026-06-19-production-code-quality-review-v19-install-path-guard-plan.md`
- `docs/dev/2026-06-19-production-code-quality-review-v18-python-interpreter-doc-fix-plan.md`
- `docs/dev/2026-06-19-awesome-skills-v17-milestone-driven-production-mode-plan.md`
- `best-project-memory/SKILL.md`
- `production-code-quality-review/SKILL.md`
- `zero-to-website-design/SKILL.md`
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
- `docs/dev/2026-06-18-zero-to-website-design-v14-workflow-doc-alignment-plan.md`
- `docs/dev/2026-06-18-awesome-skills-v15-repository-docs-line-closure-plan.md`
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
