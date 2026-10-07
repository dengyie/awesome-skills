# Changelog

All notable changes to this repository should be documented in this file.

The format is intentionally lightweight and optimized for small skill releases.

## Unreleased

### Changed

- hardened `cue-sandbox` for multi-instance fleet deployments: parameterized EasyTier overlay IP (`<CUE_OVERLAY>`) and instance name (`<CUE_INSTANCE_NAME>`) to prevent intra-mesh collision, parameterized India reverse-SSH fallback port (`<TUNNEL_REMOTE_PORT>`) with a standard systemd keepalive service template, expanded test suite credential scans to usage docs, and added root `pytest.ini` for reliable test collection
- made `cue-sandbox` executable without an Obsidian vault: probe the current host, collect missing inputs once, treat vault/`doc-lookup` as optional cache, skip India/probe/mining unless requested, and include generate-and-install commands in the references

### Added

- added `cue-sandbox` skill package: Cue sandbox access SOP for EasyTier mango-mesh TUN SSH (`ssh mesh-cue`), India reverse-SSH fallback only, Komari Linux probe with `ping_group_range`, and overlay mining without disabling Web SSH; credentials stay out of the package (placeholders only)
- added `yunzhi-cloudphone-checkin` skill package: automated daily login check-in and cloud phone space benefit card renewal (benefitConfigId: 158) for Tianyi / Play.cn Yunzhi Cloudphone, featuring zero-dependency browser DevTools console one-click script, Chrome DevTools Protocol (CDP) headless runner, direct CLI mode, Edge WAF 503 TLS fingerprint bypass, full protocol reverse engineering references, and offline signature unit tests
- added `windows-ssh-stcp` skill package: SSH into a Windows host with no inbound public port by reusing an existing frps over STCP, with loopback-only OpenSSH, NSSM keepalive, a macOS/Linux visitor, and a production pitfall runbook
- added `cloudphone-adb-tunnel` skill package: FRP STCP ADB tunnel deployment and troubleshooting for non-root Android cloud phones (Termux frpc with termux-chroot DNS, desktop visitor, phantom-process hardening), with usage guide and matrix entries
- made `cloudphone-adb-tunnel` self-contained: bundled sanitized Termux installer (v9, visitor bind port parameterized to 55556) plus spawn/keepalive scripts, frps server setup reference, and the full pitfall runbook
- added `cloudphone-adb-tunnel` consistency guard tests: bundled scripts must stay byte-identical to the installer-embedded heredocs, and the package must contain no credential literals
- hardened `cloudphone-adb-tunnel` installer (v10): early input validation for connection secrets, atomic resolv.conf write, real-frpc PID capture with procps-less fallback, spawn log preservation and keepalive.log rotation, plus a visitor-port consistency guard test

### Removed

- removed `little-lighthouse-blog-publisher` and `zero-to-website-design` skill packages, their usage guides, and all landing-page/matrix references

### Changed

- updated `muse-reverse-ssh` watchdog cadence guidance with measured production token data: 1-minute agent poll ≈26M input tokens/day, 5-minute supervisor ≈1/5 of that, 2.5-minute supervisor ≈2/5 (≈11M/day) — and recorded production's tightening to 2.5 min after repeated resident-loop deaths on a churny platform (worst-case detection window ≤2.5 min)
- updated `muse-reverse-ssh` SKILL.md Layer 3 watchdog guidance to the production two-tier pattern: a zero-cost resident loop (`scripts/health-watch-loop.sh`, new template) runs minute-level checks and self-heals on the ephemeral machine, while the external supervisor polls sparsely (5 min default) to verify loop liveness (pidfile + `/proc/<pid>/cmdline`), relaunch it detached, and read the JSON status with one fixed command — silent when healthy, logs only anomalies. Replaces the old "1-minute external poll" default after production measurement showed a 1-minute agent-driven poll burning ~7% of a weekly free quota on an idle machine (resident loop + 5-min supervisor ≈ 1/5 the usage). Added pitfalls: never `set -e` in the resident loop (degraded exit code kills it), wrap each run in `timeout`, and the post-restore re-verify must clear first-pass failures to `fixed` instead of sticking at `failed`

- updated `obsidian-doc-router` SKILL.md: multi-platform vault paths (macOS iCloud + Windows), vault-real recording directories (`Note/Project/`, `Note/AI/经验/`, `Note/Accounts/`) replacing non-existent `01.项目/`/`02.技术/`, TLDR header contract `## 速读（当前有效 · 维护于 …）`, trigger-word budget (≤15 distinctive keywords, no synonym/version enumeration), quick-section length cap (≤200 chars), and removal of stale cross-skill references

### Added

- added `muse-reverse-ssh`, a reproducible skill for exposing a machine without a public IP as a publicly reachable SSH server via a persistent reverse SSH tunnel through a VPS (two-keypair model, `GatewayPorts` setup, keepalive supervisor template, verification and failure-mode table)

- added `best-project-memory`, a repo-native continuity skill for project-state restoration, decision capture, TODO maintenance, and handoff generation
- added deterministic project-memory helper scripts for memory initialization, session-log appends, and handoff pack creation
- added `best-project-memory/scripts/compact_session.py` plus regression coverage so long-running repos can compact old session history into shorter summaries and phase recaps
- added a Phase 5 read-only integration pilot that lets `production-code-quality-review` consume `.codex-memory/` project context and relevant workstreams
- added an opt-in Level 2 memory-write path for `production-code-quality-review` so review runs can append session continuity and merge explicit follow-up TODO items
- added V9 follow-up routing hardening for `production-code-quality-review`, including urgent item routing to `In Progress` and normalized dedupe across active TODO sections
- added `zero-to-website-design`, an end-to-end website design skill for going from a blank brief to visual references, design docs, implementation, browser QA, and production delivery
- added reusable project templates for design-system docs, implementation plans, asset/data specs, page specs, visual source maps, and QA reports
- added `zero-to-website-design` usage documentation and package regression tests
- added a development plan documenting the workflow extracted from the Little Lighthouse Folk Canvas rebuild
- added `little-lighthouse-blog-publisher`, a staged publisher workflow for Little Lighthouse blog post packages
- added four-skill repository navigation across the README, skill matrix, release indexes, and Chinese overview docs
- added `zero-to-website-design` V5 template hardening for delivery-state tracking, memory-aware handoffs, and reusable website workstreams
- added a V10 documentation-sync pass that records the shipped V2 continuity surface across the main governance plan, usage docs, and repo summaries
- added V11 repair hardening for `best-project-memory`, making `init_memory.py --repair` restore partial memory layouts without overwriting existing files
- added V12 stale-todo hardening so `stale_todo_check.py` can catch active/done drift in addition to vague TODO wording

### Fixed

- tightened project-memory summary rendering in review briefs and reduced noisy workstream matching during the integration pilot
- normalized review context paths to POSIX-style separators on Windows for untracked directory and submodule expansion
- skipped POSIX install/update helper tests on Windows where Git Bash path semantics are not representative of the target shell environment
- skipped symlink-recursion coverage on Windows when the process lacks symlink creation privileges
- aligned website templates with `binding-route` and `temporary-binding` provenance language plus framework-ready versus delivery-ready reporting
- strengthened `best-project-memory/scripts/memory_lint.py` to catch missing referenced snapshots, long session history without compaction, and snapshot-to-state visibility drift

## v0.1.6 - 2026-06-17

### Added

- added a protected skill-package README that makes `production-code-quality-review/` the clear core asset
- added JSON schemas for review context and machine-readable findings
- added regression coverage for schema contract, protected asset presence, mixed working-tree line ranges, `develop` base inference, and package-manager-aware verification commands

### Fixed

- kept `working_tree` changed-line ranges aligned with branch, tracked, and untracked changes
- improved JavaScript and Python verification command suggestions for pnpm, yarn, bun, pytest, ruff, and mypy
- avoided suggesting missing JavaScript scripts when `package.json` has a known empty `scripts` object

## v0.1.5 - 2026-06-17

### Fixed

- kept installed skill copies clean by excluding `.skill-source-dir`, `__pycache__/`, and `*.pyc` during install and update
- prevented Python entrypoints from writing runtime bytecode caches into installed skill directories
- made `verify-release.sh` run with `PYTHONDONTWRITEBYTECODE=1` so release verification does not dirty the checkout

### Changed

- updated the skill description to follow a clearer `Use when...` discovery pattern
- added regression coverage for install, update, and installed-copy execution paths

## v0.1.4 - 2026-06-16

### Added

- added explicit `--base` and `--scope branch|working_tree` overrides to both review context entrypoints
- added `risk_level` and `review_mode_reason` to structured context and review briefs
- added release note templates for English and Chinese release documentation
- added regression coverage proving `branch` scope excludes uncommitted working-tree files

### Changed

- made API/network boundary changes route as high-risk specialist reviews
- routed Python repositories to the focused `python.md` reference
- synchronized English and Chinese usage docs for scope overrides and review routing
- tightened examples, quickstart, release checklist, and release index documentation

## v0.1.3 - 2026-06-16

### Fixed

- taught installed skill copies to record their source checkout via `.skill-source-dir`
- fixed `update-local-skill.sh` so running it from an installed copy refreshes from the recorded source checkout instead of deleting its own source
- added regression coverage for installed-copy update flow

### Changed

- updated install, onboarding, and release docs to describe the recorded-source refresh behavior

## v0.1.2 - 2026-06-16

### Changed

- aligned local install helpers with the current `~/.agents/skills` convention
- made legacy `~/.codex/skills` sync explicit opt-in only
- expanded README with install behavior, compact mode, and repo layout
- clarified onboarding docs around helper-based installation
- taught `update-local-skill.sh` to refresh from the recorded source checkout when invoked from an installed copy

### Removed

- tracked Python cache artifacts from the published skill tree

## v0.1.1 - 2026-06-16

### Added

- golden-path onboarding documentation
- compact review brief output mode
- local install and update helper scripts
- release checklist and troubleshooting guide
- fixture-style tests for TypeScript API, database migration, and Docker scenarios

### Changed

- tightened `SKILL.md` to reduce repeated explanation
- improved stack detection for TypeScript service repositories
- changed the Python default verification suggestion to `unittest discover`
- simplified README into a cleaner landing page

## v0.1.0 - 2026-06-16

### Added

- `production-code-quality-review` upgraded from a review SOP into a tested skill package
- deterministic repo-context scripts for:
  - review scope collection
  - changed-line mapping
  - stack detection
  - markdown review brief generation
- focused reference set for:
  - review framework
  - output contract
  - false-positive control
  - security
  - TypeScript
  - backend and integrations
  - verification and operations
  - database changes
- synthesis prompt asset
- automated tests for helper behavior
- development and release documentation

### Changed

- simplified the skill layout for maintainability
- updated README into a more product-style landing page
- documented primary user-facing entrypoints

### Removed

- `references/language-specific.md`
- granular reviewer prompt sprawl
- several overly fragmented reference files in favor of merged guides
