# Awesome Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![LINUX DO](https://img.shields.io/badge/Community-LINUX%20DO-2563eb.svg?logo=linux&logoColor=white)](https://linux.do/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

Independent Agent Skills packaged according to the Anthropic Agent Skills specification. These packages provide modular workflows for software engineering, code quality review, network tunneling, and UI components.

Compatible with OpenAI Codex, Claude Code, ZCode, Cursor, Gemini CLI, and Windsurf.

[English](README.md) | [中文说明](docs/zh/README.zh-CN.md)

---

## Acknowledgments: LINUX DO

This repository acknowledges the [LINUX DO](https://linux.do/) community. Engineering solutions throughout these packages—including log-first reproduction loops, code review criteria, and cross-NAT tunnel configurations—draw directly from technical sharing within the LINUX DO community.

---

## Architecture and Design Principles

- Reproduction before modification: Packages such as `evidence-driven-bugfix` and `production-code-quality-review` require capturing reproducible failure evidence and root-cause verification before applying code changes.
- Progressive disclosure: Each package exposes only metadata during initial discovery, costing roughly 100 tokens per skill. Operational scripts and reference documentation load only when invoked.
- Process isolation: Packages such as `codex-agent-worktree-setup` bind agent executions to isolated Git worktrees, keeping branch state decoupled from the primary working directory.
- Modular distribution: Each skill is self-contained with dedicated documentation, reference materials, and optional automation scripts.

---

## Skill Categories

### Software Engineering and Quality Assurance

- [`evidence-driven-bugfix`](evidence-driven-bugfix/): Captures reproducible failure evidence, isolates root causes, and re-verifies post-fix state.
- [`production-code-quality-review`](production-code-quality-review/): Evaluates pull requests, merge readiness, and architecture-sensitive diffs.
- [`codex-agent-worktree-setup`](codex-agent-worktree-setup/): Creates branch-bound isolated Git worktrees for agent tasks.
- [`best-project-memory`](best-project-memory/): Maintains cross-session project context, decision logs, and handoff state.

### Networking and Infrastructure Operations

- [`cloudphone-adb-tunnel`](cloudphone-adb-tunnel/): Sets up FRP STCP relays and Termux keepalive for remote ADB and scrcpy connections to non-root Android cloud phones.
- [`windows-ssh-stcp`](windows-ssh-stcp/): Configures SSH access to NAT-isolated Windows machines over existing FRP STCP relays with loopback sshd.
- [`cue-sandbox`](cue-sandbox/): Lands a Cue sandbox over EasyTier TUN SSH, with India reverse-SSH as fallback and a Komari probe.
- [`muse-reverse-ssh`](muse-reverse-ssh/): Configures reverse SSH tunnels and VPS port forwarding with process keepalive.

### UI Engineering and Assets

- [`awesome-ui-kit`](awesome-ui-kit/): Web components for AI chat interfaces, RAG search results, split-pane canvases, and agent execution monitors.
- [`split-image-assets`](split-image-assets/): Splits source images into reusable asset packages with alpha masks, layers, metadata, and quality checks.

### Search, Knowledge Base, and Automation

- [`grok-search`](grok-search/): Executes web searches, URL content extraction, and site discovery via search APIs.
- [`obsidian-doc-router`](obsidian-doc-router/): Provides routing queries and anti-orphan documentation workflows for Obsidian vaults.
- [`yunzhi-cloudphone-checkin`](yunzhi-cloudphone-checkin/): Automates daily check-ins and cloud phone renewals via browser console, Chrome CDP, or HTTP CLI.

---

## Choose a Skill

| Skill | When to use | Best for | Docs |
| --- | --- | --- | --- |
| `awesome-ui-kit` | You are assembling AI chat, RAG, canvas, or agent interfaces | copy-paste AI web components, multi-framework support | [Guide](docs/usage/awesome-ui-kit.md) |
| `best-project-memory` | You need durable repo memory across long-running work | restoring context, recording decisions, keeping TODOs and handoffs current | [Guide](docs/usage/best-project-memory.md) |
| `cloudphone-adb-tunnel` | You need ADB/scrcpy to a non-root cloud phone over the internet | FRP STCP relay, Termux frpc deployment, phantom-process hardening | [Guide](docs/usage/cloudphone-adb-tunnel.md) |
| `codex-agent-worktree-setup` | You need an isolated Codex development thread bound to a branch | protected main worktrees, branch-bound agents, detached HEAD repair | [Guide](docs/usage/codex-agent-worktree-setup.md) |
| `cue-sandbox` | You need Cue on EasyTier mesh SSH with India reverse-SSH as fallback | TUN `.81`, two-keypair SSH, Komari probe, overlay mining | [Guide](docs/usage/cue-sandbox.md) |
| `evidence-driven-bugfix` | You need a real bugfix loop instead of a guess-fix | logs-first debugging, failing evidence, root cause, re-verification | [Guide](docs/usage/evidence-driven-bugfix.md) |
| `grok-search` | You need live web access instead of offline knowledge | web search, current facts, URL reading, site page discovery | [Guide](docs/usage/grok-search.md) |
| `muse-reverse-ssh` | You need a machine without a public IP reachable over SSH from the internet | reverse SSH tunnels, VPS port forwarding, tunnel keepalive | [Guide](docs/usage/muse-reverse-ssh.md) |
| `obsidian-doc-router` | You are reading/writing Obsidian vault ops notes or topologies | router-first queries, anti-orphan documentation workflow | [Guide](docs/usage/obsidian-doc-router.md) |
| `production-code-quality-review` | You want a production-minded review of changes | PR review, merge readiness, architecture-sensitive diffs | [Review Workflows](docs/usage/review-workflows.md) |
| `split-image-assets` | You need to turn one image into reusable package assets | masks, transparent layers, previews, metadata, QA | [Guide](docs/usage/split-image-assets.md) |
| `windows-ssh-stcp` | You need SSH to a Windows host with no inbound public port | reuse an existing frps over STCP, loopback-only sshd, NSSM keepalive | [Guide](docs/usage/windows-ssh-stcp.md) |
| `yunzhi-cloudphone-checkin` | You need automated check-in and cloud phone renewal for Yunzhi Cloudphone | browser console one-click script, Chrome CDP automation, direct CLI | [Guide](docs/usage/yunzhi-cloudphone-checkin.md) |

If you are not sure which one to use, go straight to the [Skill Matrix](docs/usage/skill-matrix.md).

---

## Recommended Starting Points

- I do not know which skill to use: [Skill Matrix](docs/usage/skill-matrix.md)
- I want the fastest install path: [Quickstart](docs/usage/quickstart.md)
- I prefer Chinese docs: [中文说明](docs/zh/README.zh-CN.md)
- I want a repo walkthrough first: [Golden Path](docs/usage/golden-path.md)
- I want to review code changes: [Review Workflows](docs/usage/review-workflows.md)
- I want real-world usage examples: [Examples](docs/usage/examples.md)

---

## Install

Agent discovery paths depend on the target runtime:

| Client | User Scope | Workspace Scope |
| --- | --- | --- |
| OpenAI Codex / ZCode | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor / Windsurf / Gemini CLI | `~/.agents/skills/` | `.agents/skills/` |

### Installation Command

Copy the selected package directory into the agent discovery path:

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

Restart the agent or reload skills to complete package discovery.

For assistance choosing packages, refer to the [Skill Matrix](docs/usage/skill-matrix.md).

### Package Directory Structure

Each skill conforms to the standard layout:

```text
<skill-name>/
├── SKILL.md          # Frontmatter metadata and usage instructions
├── scripts/          # Deterministic scripts and CLI entrypoints
├── references/       # API specifications and technical reference docs
└── assets/           # Configuration files, templates, and static resources
```

---

## Docs

- [Quickstart](docs/usage/quickstart.md) — Fast installation and verification guide
- [Skill Matrix](docs/usage/skill-matrix.md) — Feature comparison and routing matrix
- [FAQ](docs/usage/faq.md) — Frequently asked questions
- [Troubleshooting](docs/usage/troubleshooting.md) — Issue diagnostics and resolution
- [Review Workflows](docs/usage/review-workflows.md) — Production code review procedures
- [Examples](docs/usage/examples.md) — Concrete usage examples
- [Chinese Overview](docs/zh/README.zh-CN.md) — Localized Chinese documentation portal
- [Release Notes](docs/releases/README.md) — Version history and release notes

---

## Repository Layout

```text
awesome-ui-kit/                     AI chat, RAG, reasoning viewer, and canvas components
best-project-memory/                Cross-session project memory, decisions, and handoffs
cloudphone-adb-tunnel/              FRP STCP relay for non-root Android cloud phone ADB
codex-agent-worktree-setup/         Branch-bound isolated Git worktrees for agent threads
cue-sandbox/                        Cue EasyTier TUN SSH, India fallback, Komari probe
evidence-driven-bugfix/             Evidence-first reproduction and bugfix loop
grok-search/                        Web search, fact verification, and URL inspection
muse-reverse-ssh/                   Reverse SSH tunnels and VPS port forwarding keepalive
obsidian-doc-router/                Obsidian vault documentation router and updates
production-code-quality-review/     Production-focused pull request review and diff audit
split-image-assets/                 Image asset decomposition, alpha masks, and packaging
windows-ssh-stcp/                   Windows SSH over FRP STCP with NSSM keepalive
yunzhi-cloudphone-checkin/          Yunzhi cloud phone daily check-in and automated renewal
docs/usage/                         Guides, matrix, troubleshooting, and examples
docs/zh/                            Chinese landing page and localized guides
docs/releases/                      Release notes and changelogs
docs/superpowers/                   Design specifications and implementation plans
tests/                              Repository-level regression test suite
```

---

## Contributing

1. Verify that new packages adhere to the Agent Skills specification with a valid `SKILL.md` frontmatter.
2. Add regression tests under the package `tests/` directory.
3. Register new packages in `docs/usage/skill-matrix.md` and repository tables.
4. Run the repository documentation test suite:
   ```bash
   python3 -m unittest discover tests -v
   ```

---

## For Maintainers

- Run repository-level docs checks with `python3 -m unittest discover tests -v`
- Run package tests from the relevant skill directory before release work
- Maintain Grok Search from `grok-search/` in this repository; local installed copies are downstream deployments
- Keep release history in [docs/releases/README.md](docs/releases/README.md)
- Keep design and implementation history in `docs/superpowers/` and `docs/dev/`
