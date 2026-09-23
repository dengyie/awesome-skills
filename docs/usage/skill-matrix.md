# Skill Matrix

Use this page when the fastest question is: "Which skill should I use first?"

For installation only, use the [Quickstart](quickstart.md).

## Quick Matrix

| Skill | When to use | Best for | Avoid when | Typical outputs | Docs |
| --- | --- | --- | --- | --- | --- |
| `awesome-ui-kit` | You are assembling AI chat, RAG, canvas, or agent interfaces | copy-paste AI web components, multi-framework support | you need backend LLM integration or generic CRUD admin tables | assembled AI pages, copy-ready component files | `docs/usage/awesome-ui-kit.md` |
| `best-project-memory` | You need durable project continuity across sessions | restoring context, keeping TODOs current, recording decisions, leaving handoffs | the work is a one-shot task with no continuity value | updated `.codex-memory/` files, session summaries, handoffs | `docs/usage/best-project-memory.md` |
| `codex-agent-worktree-setup` | You need a Codex-visible process isolated from the primary checkout | branch-bound worktrees, protected main branches, detached HEAD repair | you only need a branch in the current checkout or no new Codex thread was requested | Codex thread, isolated worktree, verified branch mapping | `docs/usage/codex-agent-worktree-setup.md` |
| `evidence-driven-bugfix` | You need a truthful bugfix workflow | logs-first debugging, failing evidence, root cause, minimal fix, fresh verification | you only want review feedback or feature planning | failing evidence chain, root-cause statement, verified fix or blocker | `docs/usage/evidence-driven-bugfix.md` |
| `grok-search` | You need live web access instead of offline knowledge | current facts, reading a known URL, discovering pages on a site | the answer is stable offline knowledge or lives in local code | search answer with merged sources, fetched page content, candidate URLs | `docs/usage/grok-search.md` |
| `muse-reverse-ssh` | You need a machine without a public IP reachable over SSH from the internet | reverse SSH tunnels, VPS port forwarding, tunnel keepalive supervision | the machine already has a public IP or you need HTTPS/browser access | working public SSH endpoint, keepalive supervisor, verification results | `docs/usage/muse-reverse-ssh.md` |
| `obsidian-doc-router` | You need accurate ops facts or are writing docs in an Obsidian vault | router-first queries, anti-orphan documentation workflow | the query is unrelated to your vault or ops notes | verified ops answers with cited notes, anti-orphan canonical entries | `docs/usage/obsidian-doc-router.md` |
| `production-code-quality-review` | You need production-minded judgment on changed code | PR review, diff triage, merge readiness, architecture-sensitive review | you need implementation or debugging instead of review | review brief, findings, risk summary, verification guidance | `docs/usage/quickstart.md`, `docs/usage/review-workflows.md` |
| `split-image-assets` | You need reusable assets instead of one flat image | object layers, masks, previews, asset manifests, QA evidence | you only need a quick crop or a fully automatic segmenter | transparent PNGs, masks, `metadata.json`, `qa_report.md`, previews | `docs/usage/split-image-assets.md` |

## Pick By Problem Type

- Need to assemble AI chat, RAG search, canvas, or agent interfaces: `awesome-ui-kit`
- Need continuity and handoff discipline: `best-project-memory`
- Need an isolated Codex thread or detached worktree repaired: `codex-agent-worktree-setup`
- Need a bug fixed through evidence and verification: `evidence-driven-bugfix`
- Need current web facts, a specific page read, or a site's pages discovered: `grok-search`
- Need a production review of changed code: `production-code-quality-review`
- Need a source image turned into reusable package assets: `split-image-assets`
- Need a machine without a public IP reachable over SSH from the internet: `muse-reverse-ssh`
- Need router-first vault reading or anti-orphan doc recording: `obsidian-doc-router`

## Pick By Expected Output

- assembled AI pages, copy-ready component files: `awesome-ui-kit`
- `.codex-memory/` updates, durable TODOs, handoff notes: `best-project-memory`
- Codex thread, isolated worktree, verified branch mapping: `codex-agent-worktree-setup`
- failing evidence, root cause, verified repair: `evidence-driven-bugfix`
- search answer with cited sources, page content, candidate URLs: `grok-search`
- review findings and merge-readiness guidance: `production-code-quality-review`
- working public SSH endpoint, keepalive supervisor, verification results: `muse-reverse-ssh`
- verified ops answers, anti-orphan canonical docs: `obsidian-doc-router`
- transparent assets, masks, previews, QA report: `split-image-assets`

## Prompt Starters

`awesome-ui-kit`

```text
Use $awesome-ui-kit to assemble a modern AI chat interface with streaming markdown and thinking blocks.
```

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

`grok-search`

```text
Use $grok-search to find the current answer to this question and give me the sources you relied on.
```

`muse-reverse-ssh`

```text
Use $muse-reverse-ssh to expose this machine without a public IP as a publicly reachable SSH server through a reverse SSH tunnel via my VPS.
```

`obsidian-doc-router`

```text
Use $obsidian-doc-router to query our infrastructure topology or record a newly deployed service without creating orphan notes.
```

`production-code-quality-review`

```text
Use $production-code-quality-review to review this change for production correctness, robustness, and merge readiness.
```

`split-image-assets`

```text
Use $split-image-assets to turn this source image into a reusable asset package with transparent layers, masks, previews, metadata, and QA.
```

## Go Next

- Need install help: [Quickstart](quickstart.md)
- Need examples: [Examples](examples.md)
- Need repo-wide guidance: [Golden Path](golden-path.md)
- Need troubleshooting: [Troubleshooting](troubleshooting.md)
