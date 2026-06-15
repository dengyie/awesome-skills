# Production Code Quality Review Redesign

Date: 2026-06-16

## Goal

Upgrade `production-code-quality-review` from a review SOP into a more complete Codex skill package with:

- stable review scope collection
- deterministic changed-line mapping
- stack-aware reference loading
- explicit false-positive controls
- a structured output contract
- lightweight reviewer orchestration prompts

## Constraints

- Keep development notes outside the skill directory.
- Preserve the skill's evidence-first, production-risk-first review posture.
- Avoid turning the skill into an overbuilt framework that is hard to maintain.
- Keep helper tooling dependency-light so it works in plain local repos.

## Target Package Shape

```text
production-code-quality-review/
  SKILL.md
  references/
    review-framework.md
    output-contract.md
    false-positive-control.md
    security.md
    typescript.md
    backend-and-integrations.md
    verification-and-operations.md
    database.md
  scripts/
    collect-review-context.py
    diff-line-map.py
    detect-stack.py
    review-entrypoint.py
    run-safe-checks.py
    review_skill_lib.py
  agents/
    openai.yaml
    synthesizer.md
  tests/
    test_review_skill_lib.py
    test_collect_review_context_cli.py
```

## Design Decisions

### 1. Keep `SKILL.md` as the dispatcher

`SKILL.md` should stay concise and high leverage. It should:

- define the mission and review standards
- force review scope collection before findings
- route the agent to references selectively
- define when to use single-agent review vs specialist prompts
- define the final report order

Detailed heuristics belong in references, not in the entry file.

### 2. Add deterministic scripts before adding complexity

The biggest functional gap is unstable input gathering. Scripts should provide:

- base branch inference
- staged / unstaged / untracked separation
- changed file list
- changed line map from `git diff --unified=0`
- stack detection from changed files and repo markers
- risk flags and recommended references
- safe verification command suggestions

The scripts should output JSON so they can be reused by humans, Codex, and future automation.

### 3. Split references by review concern

The old `language-specific.md` is too broad to be useful during targeted review. The new references should separate:

- review process
- reporting format
- false-positive suppression
- verification and operations
- backend and integration heuristics
- stack-specific frontend and database heuristics

This improves selective loading and avoids paying for unrelated guidance.

### 4. Keep only lightweight synthesis prompt assets

This repository does not need a complex multi-agent runtime yet. One reusable synthesis prompt is enough for now:

- `synthesizer.md` merges findings and removes duplicates

That keeps the package small while still making high-risk reviews more structured.

### 5. Keep validation local and dependency-light

The helper scripts should use Python standard library only. Tests should use `unittest`.

That avoids forcing contributors to install additional dependencies just to validate the skill.

## Scope For This Iteration

Included:

- skill rewrite
- README refresh
- reference expansion
- script implementation
- unit and CLI tests
- reviewer prompt assets

Excluded:

- GitHub Action integration
- automatic PR comment publishing
- external model routing
- fully automated parallel agent execution

## Success Criteria

- The package has a predictable directory structure.
- `collect-review-context.py` emits useful JSON for a live git repo.
- changed-line mapping is tested
- stack detection is tested
- review output rules are explicit enough to reduce false positives
- development notes remain isolated in `docs/dev/`
