# Awesome Skills

Reusable Codex skills with an evidence-first, production-engineering bias.

Latest release: `v0.1.6`

## Skill Packages

### `best-project-memory/`

`best-project-memory` is a lightweight continuity skill for restoring project context, keeping repo-native state files current, recording decisions, and preparing clean handoffs across sessions.

It is optimized for:

- project continuity across sessions
- repo-native memory files
- decision traceability
- actionable TODO state
- compact handoff generation
- low-friction Markdown workflows
- staged integration with other repo skills

Skill entrypoint:

```text
best-project-memory/SKILL.md
```

Repository proof points already shipped:

- `production-code-quality-review` uses it as a Level 1 read-only consumer and a Level 2 opt-in continuity writer
- `zero-to-website-design` uses it as a Level 3 governance-aware delivery workflow
- session compaction and drift-aware linting are available for long-running repos

### `production-code-quality-review/`

`production-code-quality-review` is a production-oriented review skill for pull requests, diffs, architecture-sensitive changes, reliability reviews, and merge-readiness decisions.

This directory is the product. Treat it as the protected skill layer of the repository:

- `SKILL.md` is the Codex entrypoint and discovery surface.
- `scripts/` contains deterministic review-context tooling.
- `references/` contains the review contract, heuristics, and JSON schemas.
- `agents/` contains optional synthesis and platform metadata.
- `tests/` protects the skill package, helper scripts, and install/update behavior.

Repository-level docs under `docs/` explain development and usage, but they are secondary to the shippable skill package.

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

Skill package guide:

```text
production-code-quality-review/README.md
```

### `zero-to-website-design/`

`zero-to-website-design` is an end-to-end website creation workflow for turning a blank or vague brief into visual references, design-system docs, route specs, implementation, screenshot QA, and delivery readiness.

It is optimized for:

- zero-to-one website design
- reference-image provenance
- concept generation before implementation
- design docs before code
- route-by-route implementation
- desktop/mobile browser QA
- production readiness review

Skill entrypoint:

```text
zero-to-website-design/SKILL.md
```

## Install

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Install a skill package by copying its folder:

```bash
mkdir -p ~/.agents/skills
cp -R production-code-quality-review ~/.agents/skills/
```

For the website design workflow:

```bash
mkdir -p ~/.agents/skills
cp -R zero-to-website-design ~/.agents/skills/
```

For project-memory continuity:

```bash
mkdir -p ~/.agents/skills
cp -R best-project-memory ~/.agents/skills/
```

Then start a new Codex session or reload skills so Codex can discover it.

The `production-code-quality-review` package also includes a helper install script:

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

By default the helper installs to `~/.agents/skills/production-code-quality-review`.
Set `INSTALL_LEGACY_CODEX_COPY=1` only if you explicitly want a second legacy copy under `~/.codex/skills`.
The installed copy records its source checkout so `update-local-skill.sh` can refresh from that repo path.

When running commands from this checkout, use `production-code-quality-review/scripts/...`.
When running commands from an installed copy outside the checkout, use `$HOME/.agents/skills/production-code-quality-review/scripts/...`.

## Main Entry Points

### Collect machine-readable review context

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

Optional scope controls:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo . --base origin/main --scope branch
```

### Generate a human-friendly review brief

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

### Generate a compact routing summary

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format compact
```

JSON output is available with `--format json` and follows `references/review-context.schema.json`.
Machine-readable finding records should follow `references/finding.schema.json`.

### Run the release verification bundle

```bash
bash production-code-quality-review/scripts/verify-release.sh
```

## Documentation

- [Best Project Memory](docs/usage/best-project-memory.md)
- [Zero-To-Website Design](docs/usage/zero-to-website-design.md)
- [Golden Path](docs/usage/golden-path.md)
- [Quickstart](docs/usage/quickstart.md)
- [Review Workflows](docs/usage/review-workflows.md)
- [Examples](docs/usage/examples.md)
- [FAQ](docs/usage/faq.md)
- [Release Notes](docs/releases/README.md)
- [中文文档](docs/zh/README.zh-CN.md) / [Chinese Docs](docs/zh/README.zh-CN.md)
- [中文发布说明](docs/zh/releases/README.zh-CN.md) / [Chinese Release Notes](docs/zh/releases/README.zh-CN.md)
- [中文 References 导读](docs/zh/references-guide.zh-CN.md) / [Chinese References Guide](docs/zh/references-guide.zh-CN.md)

## Local Verification

```bash
python3 -m unittest discover production-code-quality-review/tests -v
python3 -m unittest discover best-project-memory/tests -v
python3 -m unittest discover zero-to-website-design/tests -v
```

## Notes

- `language-specific.md` has been retired in favor of smaller, more focused references.
- Development notes live in `docs/dev/`.
- `review-entrypoint.py` supports `markdown`, `json`, and `compact` output.

## Repo Layout

```text
production-code-quality-review/
  SKILL.md              # Required Codex skill entrypoint
  README.md             # Skill package guide for users and maintainers
  agents/               # Platform metadata and synthesis prompt
  references/           # Review framework, output contract, heuristics, schemas
  scripts/              # Deterministic context and install/update tooling
  tests/                # Regression tests protecting the skill package
zero-to-website-design/
  SKILL.md              # Required Codex skill entrypoint
  agents/               # Platform metadata
  references/           # Website design workflow references
  assets/templates/     # Copyable project documentation templates
  tests/                # Regression tests protecting package structure
best-project-memory/
  SKILL.md              # Required Codex skill entrypoint
  agents/               # Platform metadata
  references/           # Memory schema, update policy, examples, handoff patterns
  scripts/              # Deterministic memory initialization and handoff helpers
  tests/                # Regression tests protecting package structure and scripts
docs/
  usage/                # User-facing documentation
  releases/             # Release notes and release checklist
  dev/                  # Development notes, kept separate from the skill
```
