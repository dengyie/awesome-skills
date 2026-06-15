# Production Code Quality Review Simplification

Date: 2026-06-16

## Goal

Reduce maintenance overhead and structural noise in `production-code-quality-review` without removing its core capabilities.

## Simplification Strategy

### Keep

- deterministic review-context scripts
- test coverage for script behavior
- explicit false-positive controls
- explicit output contract
- stack-aware routing

### Simplify

- reduce reference file count
- remove reviewer prompt sprawl
- shrink `SKILL.md` to a concise dispatcher
- promote only two public CLI entrypoints:
  - `collect-review-context.py`
  - `review-entrypoint.py`

## Target Structure

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
    review_skill_lib.py
    run-safe-checks.py
  agents/
    openai.yaml
    synthesizer.md
  tests/
    test_review_skill_lib.py
    test_collect_review_context_cli.py
```

## Rationale

### References

The previous split was accurate but slightly too granular for a personal skill. Merging related concerns lowers browse cost and reduces routing complexity.

### Agents

The specialist reviewer prompt files are optional prompt assets, not a required execution path. Keeping only `synthesizer.md` preserves one reusable merge prompt without forcing future maintenance across many tiny files.

### Entry Points

Publicly documented CLI usage should emphasize:

- one machine-readable scope collector
- one human-friendly review brief generator

The other scripts remain useful internal building blocks.

## Success Criteria

- fewer files in `references/` and `agents/`
- no loss of deterministic review-context behavior
- tests continue to pass
- README and `SKILL.md` point users to the simplified main path
