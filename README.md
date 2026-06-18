# Awesome Skills

Reusable Codex skills with an evidence-first, production-engineering bias.

Latest formal package release notes: `production-code-quality-review v0.1.6`

## What This Repo Contains

This repository is a multi-skill collection, not a single-package checkout.

It currently ships four Codex skills:

- `best-project-memory`: repo-native project continuity and handoff memory
- `little-lighthouse-blog-publisher`: staged publisher workflow for the Little Lighthouse blog
- `production-code-quality-review`: production-oriented review and merge-readiness workflow
- `zero-to-website-design`: design-first website delivery workflow from brief to QA

Each skill is packaged as its own folder with a `SKILL.md` entrypoint, supporting references, and package-level tests.

## Included Skills

### `best-project-memory`

Use this skill when you want Codex to restore project context at the start of work, keep repo-native memory files current, record decisions, maintain actionable TODOs, and leave a clean handoff trail for later sessions.

Best fit:

- continuing work across sessions
- keeping durable project state in the repository
- recording decisions and milestones
- generating compact handoff summaries
- integrating continuity into other repo skills

Skill entrypoint:

```text
best-project-memory/SKILL.md
```

Supporting package highlights:

- `best-project-memory/scripts/` for memory initialization, linting, compaction, and repair helpers
- `best-project-memory/references/` for schemas, examples, and operating guidance
- `docs/usage/best-project-memory.md` for the user-facing guide

### `little-lighthouse-blog-publisher`

Use this skill when you want Codex to publish, draft, update, validate, or repair posts for the Little Lighthouse blog through a staged AI workflow. It keeps the public GitHub Pages site static while Codex handles local package creation, metadata planning, asset fallback decisions, verification, review, memory updates, and commits.

Best fit:

- turning Markdown drafts or notes into Little Lighthouse blog packages
- creating draft-only post packages
- updating existing post metadata or article assets
- validating a post package before publication
- keeping blog resources in `dengyie/dengyie.github.io` while skill workflow logic lives in this repo

Skill entrypoint:

```text
little-lighthouse-blog-publisher/SKILL.md
```

Supporting package highlights:

- `little-lighthouse-blog-publisher/references/` for staged interaction, package contract, editorial, asset, verification, and commit guidance
- validates against the blog repo's `scripts/verify-blog-package.mjs` gate
- designed for `dengyie/dengyie.github.io`, with the reusable skill source maintained here
- `docs/usage/little-lighthouse-blog-publisher.md` for the user-facing guide

### `production-code-quality-review`

Use this skill when you want Codex to review working-tree changes, pull requests, or architecture-sensitive diffs with a production mindset. It emphasizes correctness, robustness, maintainability, observability, and false-positive control over style-only commentary.

Best fit:

- pull request review
- pre-merge risk assessment
- architecture-sensitive change review
- production readiness checks
- review workflows that benefit from deterministic context collection

Skill entrypoint:

```text
production-code-quality-review/SKILL.md
```

Supporting package highlights:

- `production-code-quality-review/scripts/` for review-context collection and review-entrypoint helpers
- `production-code-quality-review/references/` for schemas, heuristics, and review contracts
- `production-code-quality-review/README.md` for the package guide

### `zero-to-website-design`

Use this skill when you want Codex to turn a blank or vague website brief into a documented, design-first delivery workflow. It pushes work through references, concept generation, route planning, implementation guidance, and browser QA before sign-off.

Best fit:

- zero-to-one website design
- design documentation before code
- route-by-route implementation planning
- reference-image-backed visual direction
- desktop and mobile screenshot QA

Skill entrypoint:

```text
zero-to-website-design/SKILL.md
```

Supporting package highlights:

- `zero-to-website-design/references/` for delivery workflow references and governance
- `zero-to-website-design/assets/templates/` for reusable design and implementation templates
- `docs/usage/zero-to-website-design.md` for the user-facing guide

## Repo Layout

```text
best-project-memory/
  SKILL.md              # Required Codex skill entrypoint
  agents/               # Platform metadata
  references/           # Memory schema, update policy, examples, handoff patterns
  scripts/              # Deterministic memory initialization and handoff helpers
  tests/                # Regression tests protecting package structure and scripts
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
little-lighthouse-blog-publisher/
  SKILL.md              # Required Codex skill entrypoint
  agents/               # Platform metadata
  references/           # Blog publishing workflow contracts and checklists
docs/
  usage/                # User-facing documentation
  releases/             # Release notes and release checklist
  dev/                  # Development notes, kept separate from the skill packages
```

## Install

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Install a skill package by copying its folder:

```bash
mkdir -p ~/.agents/skills
cp -R best-project-memory ~/.agents/skills/
cp -R little-lighthouse-blog-publisher ~/.agents/skills/
cp -R production-code-quality-review ~/.agents/skills/
cp -R zero-to-website-design ~/.agents/skills/
```

Then start a new Codex session or reload skills so Codex can discover the installed package.

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

### Review context collection

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

Optional scope controls:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo . --base origin/main --scope branch
```

### Review brief generation

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

### Compact review routing output

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format compact
```

JSON output is available with `--format json` and follows `references/review-context.schema.json`.
Machine-readable finding records should follow `references/finding.schema.json`.

### Release verification bundle

```bash
bash production-code-quality-review/scripts/verify-release.sh
```

## Documentation

Repository overview and usage:

- [Skill Matrix](docs/usage/skill-matrix.md)
- [Best Project Memory](docs/usage/best-project-memory.md)
- [Little Lighthouse Blog Publisher](docs/usage/little-lighthouse-blog-publisher.md)
- [Zero-To-Website Design](docs/usage/zero-to-website-design.md)
- [Golden Path](docs/usage/golden-path.md)
- [Quickstart](docs/usage/quickstart.md)
- [Review Workflows](docs/usage/review-workflows.md)
- [Examples](docs/usage/examples.md)
- [FAQ](docs/usage/faq.md)
- [Troubleshooting](docs/usage/troubleshooting.md)
- [Release Notes](docs/releases/README.md)

Current formal versioned release notes are published for `production-code-quality-review`.
For `best-project-memory`, `little-lighthouse-blog-publisher`, and `zero-to-website-design`, use the package usage guides plus `docs/dev/` staged development notes.

Chinese documentation:

- [Chinese Overview](docs/zh/README.zh-CN.md)
- [Chinese Release Notes](docs/zh/releases/README.zh-CN.md)
- [Chinese References Guide](docs/zh/references-guide.zh-CN.md)

## Local Verification

```bash
python3 -m unittest discover production-code-quality-review/tests -v
python3 -m unittest discover best-project-memory/tests -v
python3 -m unittest discover little-lighthouse-blog-publisher/tests -v
python3 -m unittest discover zero-to-website-design/tests -v
```

## Notes

- `language-specific.md` has been retired in favor of smaller, more focused references.
- Development notes live in `docs/dev/`.
- `review-entrypoint.py` supports `markdown`, `json`, and `compact` output.
