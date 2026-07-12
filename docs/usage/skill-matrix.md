# Skill Matrix

Use this page when the fastest question is: "Which skill should I use first?"

For installation only, use the [Quickstart](quickstart.md).

## Quick Matrix

| Skill | When to use | Best for | Avoid when | Typical outputs | Docs |
| --- | --- | --- | --- | --- | --- |
| `best-project-memory` | You need durable project continuity across sessions | restoring context, keeping TODOs current, recording decisions, leaving handoffs | the work is a one-shot task with no continuity value | updated `.codex-memory/` files, session summaries, handoffs | `docs/usage/best-project-memory.md` |
| `codex-agent-worktree-setup` | You need a Codex-visible process isolated from the primary checkout | branch-bound worktrees, protected main branches, detached HEAD repair | you only need a branch in the current checkout or no new Codex thread was requested | Codex thread, isolated worktree, verified branch mapping | `docs/usage/codex-agent-worktree-setup.md` |
| `evidence-driven-bugfix` | You need a truthful bugfix workflow | logs-first debugging, failing evidence, root cause, minimal fix, fresh verification | you only want review feedback or feature planning | failing evidence chain, root-cause statement, verified fix or blocker | `docs/usage/evidence-driven-bugfix.md` |
| `little-lighthouse-blog-publisher` | You are publishing content into the Little Lighthouse blog repo | staged post packaging, metadata confirmation, verification, publish-ready handoff | the target is a generic CMS or a non-Little-Lighthouse site | Markdown package, metadata plan, verification results, publish flow | `docs/usage/little-lighthouse-blog-publisher.md` |
| `production-code-quality-review` | You need production-minded judgment on changed code | PR review, diff triage, merge readiness, architecture-sensitive review | you need implementation or debugging instead of review | review brief, findings, risk summary, verification guidance | `docs/usage/quickstart.md`, `docs/usage/review-workflows.md` |
| `split-image-assets` | You need reusable assets instead of one flat image | object layers, masks, previews, asset manifests, QA evidence | you only need a quick crop or a fully automatic segmenter | transparent PNGs, masks, `metadata.json`, `qa_report.md`, previews | `docs/usage/split-image-assets.md` |
| `zero-to-website-design` | You need a design-first website workflow | direction setting, route planning, implementation guidance, browser QA | the change is a tiny component edit or a backend-only task | design docs, route plans, implementation map, QA artifacts | `docs/usage/zero-to-website-design.md` |

## Pick By Problem Type

- Need continuity and handoff discipline: `best-project-memory`
- Need an isolated Codex thread or detached worktree repaired: `codex-agent-worktree-setup`
- Need a bug fixed through evidence and verification: `evidence-driven-bugfix`
- Need a production review of changed code: `production-code-quality-review`
- Need a source image turned into reusable package assets: `split-image-assets`
- Need to publish into the Little Lighthouse blog: `little-lighthouse-blog-publisher`
- Need to design and deliver a website from a vague brief or references: `zero-to-website-design`

## Pick By Expected Output

- `.codex-memory/` updates, durable TODOs, handoff notes: `best-project-memory`
- Codex thread, isolated worktree, verified branch mapping: `codex-agent-worktree-setup`
- failing evidence, root cause, verified repair: `evidence-driven-bugfix`
- review findings and merge-readiness guidance: `production-code-quality-review`
- blog post package and publication verification: `little-lighthouse-blog-publisher`
- transparent assets, masks, previews, QA report: `split-image-assets`
- design docs, implementation map, browser QA: `zero-to-website-design`

## Prompt Starters

`best-project-memory`

```text
Use $best-project-memory to restore this repo's current objective, decisions, active TODOs, and latest session summary before I continue.
```

`codex-agent-worktree-setup`

```text
Use $codex-agent-worktree-setup to create an isolated Codex worktree on the requested branch while keeping the primary main worktree unchanged.
```

`evidence-driven-bugfix`

```text
Use $evidence-driven-bugfix to fix this failure by first capturing logs, securing failing evidence, tracing the root cause, and only reporting success after fresh verification.
```

`little-lighthouse-blog-publisher`

```text
Use $little-lighthouse-blog-publisher to publish this Little Lighthouse Markdown draft as a blog post.
```

`production-code-quality-review`

```text
Use $production-code-quality-review to review this change for production correctness, robustness, and merge readiness.
```

`split-image-assets`

```text
Use $split-image-assets to turn this source image into a reusable asset package with transparent layers, masks, previews, metadata, and QA.
```

`zero-to-website-design`

```text
Use $zero-to-website-design to turn this website brief and reference set into design docs, implementation guidance, and browser QA.
```

## Go Next

- Need install help: [Quickstart](quickstart.md)
- Need examples: [Examples](examples.md)
- Need repo-wide guidance: [Golden Path](golden-path.md)
- Need troubleshooting: [Troubleshooting](troubleshooting.md)
