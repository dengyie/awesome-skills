# Zero-To-Website Design V7 Provenance Contract Hardening Plan

> Status: Implemented and verified in working tree
> Target package: `zero-to-website-design`
> Phase type: provenance and template contract hardening

## Goal

Close the remaining contract gap between the shipped historical-mock workflow and the provenance artifacts that projects actually fill in.

After V6, the package now says:

- repo-owned historical images can drive `Framework Ready` delivery
- `temporary-binding` assets must declare what they control
- upgrade triggers and residual ownership must stay visible

But the core provenance references and templates still under-specify some of that behavior, especially where projects record authority decisions.

This phase should make the provenance contract fully consistent across:

- `references/visual-provenance.md`
- `assets/templates/visual-source-map.md`
- the related regression tests
- usage and memory surfaces when needed

## Why This Phase

The current package is close, but there is still one real mismatch:

1. `SKILL.md`, historical-mock guidance, and framework-first guidance now ask for stronger ownership detail
2. the templates that teams actually fill in still capture only the older, lighter provenance surface

That means a project can technically follow the newer skill instructions while still producing weaker docs than the workflow now expects.

This is exactly the kind of drift the repository has been trying to eliminate.

## Target Outcome

When this phase is done, a project using `zero-to-website-design` should be able to record provenance decisions without guesswork.

For any `binding-route` or `temporary-binding` image, the artifacts should make it obvious:

- why this image is authoritative
- what route or section it controls
- whether it controls route composition, slot shape, or only texture/palette
- what milestone it supports
- what would trigger replacement
- what known limitations remain

## Scope

In scope:

- strengthen `references/visual-provenance.md`
- strengthen `assets/templates/visual-source-map.md`
- update tests that guard the provenance contract
- update usage or memory docs only when needed to keep the public contract consistent
- run validation, tests, and production review

Out of scope:

- changing the high-level workflow order again
- adding new status values
- introducing automation scripts
- changing unrelated `best-project-memory` or review package behavior

## Concrete Gaps To Close

### 1. `visual-provenance.md` is still too light on binding detail

It defines statuses and source methods well, but it does not yet strongly encode:

- milestone supported
- authority reason
- replacement trigger
- the difference between route composition ownership and slot-only ownership

### 2. `visual-source-map.md` still reflects the older row shape

The template currently captures:

- asset
- source method
- date
- status
- controls
- viewport
- notes

That is useful, but after V6 it should likely also capture:

- authority reason
- milestone supported
- replacement trigger

### 3. Tests do not yet lock the stricter provenance artifact shape

Current tests protect status names and high-level language, but not the full row/field expectations that real project docs should now follow.

## Proposed Changes

### `references/visual-provenance.md`

Add stronger rules for `binding-route` and `temporary-binding` images:

- `authority reason`
- `milestone supported`
- `replacement trigger`
- `ownership scope`

Add explicit ownership scope examples:

- whole route composition
- section composition
- illustration slot shape
- palette/texture only

### `assets/templates/visual-source-map.md`

Expand the table to include:

- `Authority Reason`
- `Milestone Supported`
- `Replacement Trigger`

Expand the authority notes section to include:

- route composition owners
- slot-only owners
- temporary-binding upgrades in flight

### Tests

Add or tighten checks so the package proves:

- provenance docs describe ownership scope
- provenance docs describe authority reason / milestone / replacement trigger
- visual-source-map template exposes the stricter fields
- usage/docs still align with the shipped provenance contract

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- `visual-provenance.md` fully reflects the stronger V6 ownership contract
- `visual-source-map.md` can capture all required provenance fields without improvisation
- regression tests protect the stricter provenance contract
- validation passes
- production review passes with no confirmed blocking issue

## Suggested Commit Shape

- `feat(阶段15): harden provenance contract`
