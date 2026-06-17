# Zero-To-Website Design V5 Memory-Aware Templates Plan

> Status: In progress.
> Target package: `zero-to-website-design`
> Phase type: template and artifact hardening

## Goal

Bring the package templates into line with the V3 and V4 workflow contract so projects can actually produce memory-aware delivery artifacts instead of only reading about them.

This phase should make the shipped templates reflect:

1. the newer provenance statuses such as `approved-direction`, `binding-route`, and `temporary-binding`
2. framework-ready versus visual-delivery-ready reporting
3. project-memory-aware implementation, QA, and handoff notes

## Why This Phase

The package contract has advanced faster than some of the templates.

Current gaps:

- `visual-source-map.md` still documents the older `approved` / `binding` wording
- `implementation-plan.md`, `qa-report.md`, and `page-spec.md` do not yet capture memory-aware delivery state well
- the package encourages Level 3 memory behavior, but the main reusable artifacts do not help the user preserve that state

This creates drift between:

- what `SKILL.md` and references say
- what project docs created from templates actually look like

## Scope

In scope:

- update `assets/templates/visual-source-map.md` to match V3 provenance semantics
- update `assets/templates/implementation-plan.md` with memory-aware execution and milestone fields
- update `assets/templates/qa-report.md` with framework/delivery status and handoff-style reporting
- update `assets/templates/page-spec.md` with route memory and milestone fields
- add a dedicated template for a website delivery workstream
- expand tests so the template contract is protected
- run tests, validation, and `production-code-quality-review`
- fix confirmed findings

Out of scope:

- adding executable automation scripts to generate these project docs
- changing repository-wide markdown conventions
- creating full sample website projects in this repository

## Proposed Template Changes

### `visual-source-map.md`

Update status legend to:

- `exploratory`
- `candidate`
- `approved-direction`
- `binding-route`
- `temporary-binding`
- `obsolete`

Also add a note that `temporary-binding` assets require upgrade tracking.

### `implementation-plan.md`

Add fields for:

- current milestone target (`Framework Ready` or `Visual Delivery Ready`)
- workstream name
- memory update plan
- decision promotion triggers
- handoff trigger

### `qa-report.md`

Add fields for:

- framework-ready versus delivery-ready status
- temporary-binding assets still in use
- handoff-needed flag
- next-session follow-up

### `page-spec.md`

Add fields for:

- current route milestone
- related workstream
- temporary-binding assets
- handoff-sensitive gaps

### New template: `website-workstream.md`

Add a reusable project document aligned with `.codex-memory/workstreams/*.md` but phrased for website delivery.

Suggested sections:

- Objective
- Current State
- Routes In Scope
- Assets In Scope
- QA State
- Blockers
- Next Actions
- Validation

## Package Changes

### Add

- `zero-to-website-design/assets/templates/website-workstream.md`
- `docs/dev/2026-06-17-zero-to-website-design-v5-memory-aware-templates-plan.md`

### Modify

- `zero-to-website-design/assets/templates/visual-source-map.md`
- `zero-to-website-design/assets/templates/implementation-plan.md`
- `zero-to-website-design/assets/templates/qa-report.md`
- `zero-to-website-design/assets/templates/page-spec.md`
- `zero-to-website-design/SKILL.md` if template routing needs to mention the new workstream template
- `docs/usage/zero-to-website-design.md`
- `zero-to-website-design/tests/test_skill_package.py`
- `CHANGELOG.md`

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python -m unittest discover production-code-quality-review/tests -v`
- `python %USERPROFILE%/.codex/skills/.system/skill-creator/scripts/quick_validate.py E:/project/blog/awesome-skills/zero-to-website-design`
- `python production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown`

## Acceptance Criteria

- template status language matches the V3 provenance contract
- templates now expose framework-ready versus delivery-ready state where relevant
- a reusable website workstream template exists
- tests prove the template contract and updated status language
- validation passes
- production review is run and confirmed findings are fixed

## Tasks

- [ ] Update the existing templates.
- [ ] Add the website workstream template.
- [ ] Update usage docs and template routing if needed.
- [ ] Expand regression tests.
- [ ] Run validation and tests.
- [ ] Run production review and fix findings.
- [ ] Update project memory, commit, and push.
