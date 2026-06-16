# Changelog

All notable changes to this repository should be documented in this file.

The format is intentionally lightweight and optimized for small skill releases.

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
