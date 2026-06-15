# Awesome Skills

Reusable Codex skills with an evidence-first, production-engineering bias.

## Included Skill

### production-code-quality-review

`production-code-quality-review` is a production-oriented review skill for pull requests, diffs, architecture-sensitive changes, reliability reviews, and merge-readiness decisions.

It is optimized for:

- correctness
- robustness
- maintainability
- architecture fit
- scalability
- observability
- test quality
- false-positive control

Skill entrypoint:

```text
production-code-quality-review/SKILL.md
```

## What Makes It Useful

This skill is designed to be more than a prompt:

- deterministic repo context collection before findings
- changed-line mapping from git diffs
- stack-aware review reference routing
- explicit false-positive suppression rules
- structured review output contract
- lightweight synthesis support for higher-risk reviews

## Package Structure

Each skill lives in its own directory:

```text
skill-name/
  SKILL.md
  references/
  scripts/
  agents/
  tests/
```

For `production-code-quality-review`:

- `SKILL.md` is the dispatcher and workflow contract
- `references/` holds the focused deep-dive review guides
- `scripts/` holds deterministic helper tooling
- `agents/` holds agent metadata and a synthesis prompt
- `tests/` validates helper behavior

Development notes stay outside the skill package in `docs/dev/`.

## Install

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Example:

```bash
mkdir -p ~/.agents/skills
cp -R production-code-quality-review ~/.agents/skills/
```

Then start a new Codex session or reload skills so Codex can discover it.

## Main Entry Points

The two primary user-facing scripts are:

### 1. Collect machine-readable review context

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

This returns structured JSON for:

- base branch or fallback scope
- staged, unstaged, and untracked files
- changed files and changed line ranges
- detected stack
- risk flags
- suggested references
- safe verification commands

### 2. Generate a human-friendly review brief

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

This produces a concise review brief with:

- scope summary
- routing mode
- suggested references
- changed-line summary
- verification commands

## Local Verification

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

## Notes

- `language-specific.md` has been retired in favor of smaller, more focused references.
- Lower-level helper scripts remain available for custom automation, but most users only need `collect-review-context.py` and `review-entrypoint.py`.
