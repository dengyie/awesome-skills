# Awesome Skills

Reusable Codex skills for evidence-first, production-minded project work.

This repository ships independent skill packages. Start by choosing the one that matches your problem, then install only what you need.

## Choose a Skill

| Skill | When to use | Best for | Docs |
| --- | --- | --- | --- |
| `best-project-memory` | You need durable repo memory across long-running work | restoring context, recording decisions, keeping TODOs and handoffs current | [Guide](docs/usage/best-project-memory.md) |
| `codex-agent-worktree-setup` | You need an isolated Codex development thread bound to a branch | protected main worktrees, branch-bound agents, detached HEAD repair | [Guide](docs/usage/codex-agent-worktree-setup.md) |
| `evidence-driven-bugfix` | You need a real bugfix loop instead of a guess-fix | logs-first debugging, failing evidence, root cause, re-verification | [Guide](docs/usage/evidence-driven-bugfix.md) |
| `little-lighthouse-blog-publisher` | You are publishing content into the Little Lighthouse blog repo | staged blog package creation, validation, and publication | [Guide](docs/usage/little-lighthouse-blog-publisher.md) |
| `production-code-quality-review` | You want a production-minded review of changes | PR review, merge readiness, architecture-sensitive diffs | [Review Workflows](docs/usage/review-workflows.md) |
| `split-image-assets` | You need to turn one image into reusable package assets | masks, transparent layers, previews, metadata, QA | [Guide](docs/usage/split-image-assets.md) |
| `zero-to-website-design` | You need to go from vague website brief to delivery workflow | website design direction, route plans, implementation, QA | [Guide](docs/usage/zero-to-website-design.md) |

If you are not sure which one to use, go straight to the [Skill Matrix](docs/usage/skill-matrix.md).

## Recommended Starting Points

- I do not know which skill to use: [Skill Matrix](docs/usage/skill-matrix.md)
- I want the fastest install path: [Quickstart](docs/usage/quickstart.md)
- I prefer Chinese docs: [中文说明](docs/zh/README.zh-CN.md)
- I want a repo walkthrough first: [Golden Path](docs/usage/golden-path.md)

## Install

Current OpenAI Codex docs use:

- user scope: `$HOME/.agents/skills`
- repo scope: `.agents/skills`

Install one skill by copying its folder:

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

Then restart Codex or reload skills so the new package is discovered.

If you want help deciding which folder to copy, start with the [Skill Matrix](docs/usage/skill-matrix.md).

## Docs

- [Quickstart](docs/usage/quickstart.md)
- [Skill Matrix](docs/usage/skill-matrix.md)
- [FAQ](docs/usage/faq.md)
- [Troubleshooting](docs/usage/troubleshooting.md)
- [Review Workflows](docs/usage/review-workflows.md)
- [Examples](docs/usage/examples.md)
- [Chinese Overview](docs/zh/README.zh-CN.md)
- [Release Notes](docs/releases/README.md)

## Repository Layout

```text
best-project-memory/                 skill package
codex-agent-worktree-setup/         skill package
evidence-driven-bugfix/             skill package
little-lighthouse-blog-publisher/   skill package
production-code-quality-review/     skill package
split-image-assets/                 skill package
zero-to-website-design/             skill package
docs/usage/                         newcomer and usage guides
docs/zh/                            Chinese entry docs
docs/releases/                      release notes
docs/superpowers/                   design specs and implementation plans
tests/                              repository-level regression checks
```

## For Maintainers

- Run repository-level docs checks with `python3 -m unittest discover tests -v`
- Run package tests from the relevant skill directory before release work
- Keep release history in [docs/releases/README.md](docs/releases/README.md)
- Keep design and implementation history in `docs/superpowers/` and `docs/dev/`
