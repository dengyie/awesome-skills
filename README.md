# Awesome Skills

Reusable Codex skills with an evidence-first, production-engineering bias.

Latest release: `v0.1.5`

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

Helper install script:

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

By default the helper installs to `~/.agents/skills/production-code-quality-review`.
Set `INSTALL_LEGACY_CODEX_COPY=1` only if you explicitly want a second legacy copy under `~/.codex/skills`.
The installed copy records its source checkout so `update-local-skill.sh` can refresh from that repo path.

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

### Run the release verification bundle

```bash
bash production-code-quality-review/scripts/verify-release.sh
```

## Documentation

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
```

## Notes

- `language-specific.md` has been retired in favor of smaller, more focused references.
- Development notes live in `docs/dev/`.
- `review-entrypoint.py` supports `markdown`, `json`, and `compact` output.

## Repo Layout

```text
production-code-quality-review/
  SKILL.md
  scripts/
  references/
  agents/
  tests/
docs/
  usage/
  releases/
  dev/
```
