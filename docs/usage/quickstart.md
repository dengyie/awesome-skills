# Quickstart

`production-code-quality-review` is designed to help Codex review code with a production-engineering mindset while grounding findings in deterministic repo context.

## 1. Install The Skill

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Install locally:

```bash
mkdir -p ~/.agents/skills
cp -R production-code-quality-review ~/.agents/skills/
```

Then restart Codex or reload skills.

Or use the helper:

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

The helper defaults to `~/.agents/skills`. Set `INSTALL_LEGACY_CODEX_COPY=1` only if you explicitly want a second legacy copy under `~/.codex/skills`.
The installed copy also records its source checkout so the update helper can refresh from the original repo path.

Use `production-code-quality-review/scripts/...` when running from this checkout.
Use `$HOME/.agents/skills/production-code-quality-review/scripts/...` when running from an installed copy outside the checkout.

## 2. Collect Review Context

Run:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

This returns JSON that includes:

- base branch or fallback scope
- staged, unstaged, and untracked files
- changed files
- changed-line ranges
- detected stack
- risk flags
- suggested references
- safe verification commands

This is the main deterministic entrypoint. The smaller helper scripts expose subsets of the same context for narrow automation or debugging.
Use `--base <ref>` or `--scope branch|working_tree` when you need to pin the review baseline.
For automation, `review-entrypoint.py --format json` follows `references/review-context.schema.json`.

## 3. Generate A Review Brief

Run:

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

This produces a concise brief for the current review scope with:

- scope summary
- routing mode
- suggested references
- changed-line summary
- verification commands

## 4. Use The Skill In Codex

Prompt Codex with something like:

```text
Use $production-code-quality-review to review this change for production correctness and merge readiness.
```

The skill is strongest when Codex can also inspect the local repo or diff.

## 5. Verify The Package

Run:

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

This validates the deterministic helper behavior.

If you want one command that bundles the main release checks, run:

```bash
bash production-code-quality-review/scripts/verify-release.sh
```
