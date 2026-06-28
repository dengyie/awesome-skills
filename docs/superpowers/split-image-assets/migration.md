# Split Image Assets Doc Migration

Date: 2026-06-29

## Purpose

This note records the documentation-system migration for `split-image-assets`.

The repository previously kept `split-image-assets` design and plan history as dated files under:

- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

That made the package easy to evolve but too easy to fragment. Multiple files could look authoritative at the same time.

The repository now uses:

- `docs/superpowers/split-image-assets/README.md`
- `docs/superpowers/split-image-assets/design.md`
- `docs/superpowers/split-image-assets/implementation-plan.md`

## Migration Rule

From this point on:

- new `split-image-assets` design work goes into `design.md`
- new `split-image-assets` execution planning goes into `implementation-plan.md`
- old split-image-assets dated spec/plan files are not extended
- package docs and code must converge to this directory before further behavioral changes proceed

## Retired Documents

The following dated split-image-assets docs were retired during this migration:

- `docs/superpowers/specs/2026-06-23-split-image-assets-design.md`
- `docs/superpowers/specs/2026-06-23-split-image-assets-pipeline-refactor-design.md`
- `docs/superpowers/specs/2026-06-28-split-image-assets-interaction-framework-design.md`
- `docs/superpowers/specs/2026-06-28-split-image-assets-asset-value-scoring-design.md`
- `docs/superpowers/specs/2026-06-29-split-image-assets-usability-redesign-design.md`
- `docs/superpowers/plans/2026-06-23-split-image-assets.md`
- `docs/superpowers/plans/2026-06-28-split-image-assets-interaction-framework.md`
- `docs/superpowers/plans/2026-06-28-split-image-assets-asset-value-scoring-implementation-plan.md`
- `docs/superpowers/plans/2026-06-29-split-image-assets-usability-redesign-implementation-plan.md`

Their design intent has been absorbed into the canonical files in this directory.
