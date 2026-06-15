# Changelog

All notable changes to this repository should be documented in this file.

The format is intentionally lightweight and optimized for small skill releases.

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
