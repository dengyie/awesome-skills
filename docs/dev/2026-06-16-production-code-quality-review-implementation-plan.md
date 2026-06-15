# Production Code Quality Review Implementation Plan

Date: 2026-06-16

## Goal

Ship a usable, testable redesign of `production-code-quality-review` with isolated development documentation and no changes mixed into unrelated directories.

## Architecture Summary

The skill will use a three-layer structure:

1. `SKILL.md` for workflow and routing
2. `references/` for deep review guidance
3. `scripts/` for deterministic repo analysis

Optional specialist review prompts in `agents/` act as reusable sub-review lenses for higher-risk changes.

## Work Breakdown

### Task 1: Add documentation and test scaffolding

Files:

- Create: `docs/dev/2026-06-16-production-code-quality-review-redesign.md`
- Create: `docs/dev/2026-06-16-production-code-quality-review-implementation-plan.md`
- Create: `production-code-quality-review/tests/test_review_skill_lib.py`
- Create: `production-code-quality-review/tests/test_collect_review_context_cli.py`

Done when:

- development docs describe the intended package shape
- tests describe expected script behavior before implementation exists

### Task 2: Implement deterministic review context tooling

Files:

- Create: `production-code-quality-review/scripts/review_skill_lib.py`
- Create: `production-code-quality-review/scripts/diff-line-map.py`
- Create: `production-code-quality-review/scripts/detect-stack.py`
- Create: `production-code-quality-review/scripts/collect-review-context.py`
- Create: `production-code-quality-review/scripts/run-safe-checks.py`

Done when:

- the scripts return JSON
- unit tests pass
- the CLI integration test passes against a temp git repo

### Task 3: Rewrite skill entrypoint and references

Files:

- Modify: `production-code-quality-review/SKILL.md`
- Modify: `production-code-quality-review/references/review-framework.md`
- Modify: `production-code-quality-review/references/security.md`
- Delete: `production-code-quality-review/references/language-specific.md`
- Create: `production-code-quality-review/references/output-contract.md`
- Create: `production-code-quality-review/references/false-positive-control.md`
- Create: `production-code-quality-review/references/verification-and-operations.md`
- Create: `production-code-quality-review/references/typescript.md`
- Create: `production-code-quality-review/references/backend-and-integrations.md`
- Create: `production-code-quality-review/references/database.md`

Done when:

- `SKILL.md` instructs the agent to collect review context first
- references are split by concern and stack
- output schema and false-positive rules are explicit

### Task 4: Add lightweight agent prompts and refresh README

Files:

- Modify: `production-code-quality-review/agents/openai.yaml`
- Create: `production-code-quality-review/agents/synthesizer.md`
- Modify: `README.md`

Done when:

- the repo documents current install guidance
- the skill package includes reusable specialist prompts

### Task 5: Verify everything end to end

Verification commands:

```bash
python3 -m unittest discover production-code-quality-review/tests -v
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
python3 production-code-quality-review/scripts/detect-stack.py --repo .
python3 production-code-quality-review/scripts/diff-line-map.py --repo .
python3 production-code-quality-review/scripts/run-safe-checks.py --repo .
```

Done when:

- tests pass
- helper CLIs return structured output
- repo status shows only intended changes
