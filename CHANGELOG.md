# Changelog

All notable changes to this repository should be documented in this file.

The format is intentionally lightweight and optimized for small skill releases.

## Unreleased

### Added

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
- added `zero-to-website-design` V5 template hardening for delivery-state tracking, memory-aware handoffs, and reusable website workstreams
- added a V10 documentation-sync pass that records the shipped V2 continuity surface across the main governance plan, usage docs, and repo summaries

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
