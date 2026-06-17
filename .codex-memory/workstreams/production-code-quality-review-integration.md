# Workstream

## Objective
- Pilot a Level 1 integration where `production-code-quality-review` reads `.codex-memory` and surfaces relevant project context in review setup.

## Current State
- `collect_review_context()` now emits `project_memory`.
- Review briefs expose whether project memory is present and list matched workstreams when relevant.
- Schema and test coverage were expanded to lock the new contract in place.

## Blockers
- None.

## Files
- `production-code-quality-review/scripts/review_skill_lib.py`
- `production-code-quality-review/references/review-context.schema.json`
- `production-code-quality-review/tests/test_collect_review_context_cli.py`
- `production-code-quality-review/tests/test_review_skill_lib.py`
- `production-code-quality-review/tests/golden/review-brief-markdown.md`
- `production-code-quality-review/tests/golden/review-brief-compact.txt`

## Next Actions
- [ ] Record the Phase 5 delivery details in the V2 development document.
- [ ] Choose whether the next iteration adds append/update behavior or integrates another skill.

## Validation
- `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`
