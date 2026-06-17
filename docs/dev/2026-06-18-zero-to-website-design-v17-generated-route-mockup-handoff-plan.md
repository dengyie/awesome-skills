# Zero-To-Website Design V17 Generated Route Mockup Handoff Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: concept-to-route handoff hardening

## Goal

Tighten the package's generated route-mockup handoff contract so a chosen concept direction can be expanded into route-specific implementation authority without relying on private chat memory or unrecorded judgment.

The package already has stronger rules for when generation is justified, how status escalation works, how provenance is recorded, and how temporary assets are tracked after they exist. The softer gap is the moment between "the user chose this direction" and "these route-specific mockups now legitimately guide implementation."

## Why This Phase

`zero-to-website-design` already requires:

- generation entry conditions
- concept status escalation
- route family or system scope for approved directions
- explicit route ownership before `binding-route`
- upgrade and replacement recording for generated assets

But the current route-mockup expansion guidance still under-records several implementation-critical facts:

- which route set must be expanded before coding can safely begin
- whether the selected concept already covers desktop and mobile for the hardest routes
- which route mockups inherit authority directly from the chosen concept versus needing a separate generated pass
- when a generated route mockup is only `temporary-binding` versus ready to become `binding-route`
- what another session must verify before implementation can treat the generated route mockup as trustworthy

That leaves room for a project to have a chosen concept and some generated images, but still force the next session to infer how far authority really traveled from the broad concept into route-scoped implementation.

## Target Outcome

After this phase, the package should make it natural to preserve:

- route-mockup coverage expectations after concept selection
- hardest-route and hardest-viewport expansion requirements
- explicit inheritance or non-inheritance of authority from chosen concept to route mockup
- route-mockup escalation rules for `temporary-binding` versus `binding-route`
- next verification target before implementation begins from generated route assets

## Scope

In scope:

- harden `zero-to-website-design/references/concept-generation.md`
- harden `zero-to-website-design/references/visual-provenance.md`
- harden `zero-to-website-design/references/framework-first-delivery.md`
- harden `zero-to-website-design/assets/templates/visual-source-map.md`
- harden `zero-to-website-design/assets/templates/mock-asset-pass.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new automation scripts
- changes to global route evidence statuses
- changes to content-readiness or metadata integrity semantics
- new template files

## Concrete Gaps To Close

### 1. Chosen concepts do not yet force a concrete route-mockup expansion record

The current workflow says to extend the selected direction into route-specific mockups, but it does not yet strongly name which routes and viewports must be covered before implementation starts from generated assets.

### 2. Authority inheritance is still too implicit

A chosen direction may inspire several routes, but that does not automatically mean every route mockup is equally authoritative. The package should explicitly say when route authority is inherited, when a new route mockup is required, and when the result can only be `temporary-binding`.

### 3. Route-mockup verification still lacks a clear next-step contract

Before coding, another session should be able to see which generated route mockups still need desktop/mobile validation, route ownership confirmation, or stronger replacement planning.

## Proposed Changes

### `references/concept-generation.md`

Clarify that after concept selection the workflow should preserve:

- required route set for expansion
- hardest route / hardest viewport coverage
- whether each route mockup inherits or overrides the chosen concept
- the next verification target before implementation begins

### `references/visual-provenance.md`

Clarify that generated route mockups should record:

- whether authority is inherited from the selected concept or granted by a route-specific pass
- route-mockup coverage status
- escalation threshold for `temporary-binding` versus `binding-route`

### `references/framework-first-delivery.md`

Clarify that framework-first delivery from generated route assets still depends on explicit route-mockup ownership, coverage notes, and next verification targets.

### `assets/templates/visual-source-map.md`

Add fields or notes for:

- inherited from selected concept
- route-mockup coverage
- escalation target

### `assets/templates/mock-asset-pass.md`

Add fields for:

- concept selected from
- required route expansion
- hardest viewport covered
- route-mockup escalation target

### `docs/usage/zero-to-website-design.md`

Add a compact generated-route-mockup section that explains a chosen concept is not enough by itself; another session should be able to see which route mockups exist, what authority they hold, and what must still be checked before coding.

### Tests

Expand package tests so the repo proves:

- concept-generation guidance now mentions route-mockup coverage, inheritance, escalation target, and next verification target
- provenance and framework-first references mention the generated route-mockup handoff more explicitly
- source-map and mock-asset templates carry the new fields
- usage docs explain the generated route-mockup continuity expectation

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- generated concept guidance now preserves route-mockup expansion and authority inheritance more explicitly
- provenance and framework-first references expose the stronger generated route-mockup contract
- source-map and mock-asset templates carry the new handoff fields
- usage docs expose the stronger expectation
- tests lock the new contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use generated route-mockup handoff hardening as the V17 stage for `zero-to-website-design`.
- Rationale: The package's generation and provenance contracts are already much stronger, but the expansion from approved concept to route-specific implementation authority is still not explicit enough for long-running, resumable website work.
- Risk: The new route-mockup coverage language could feel heavy for very small sites with one simple page.
- Mitigation: Keep the new fields focused on route coverage, inherited authority, and verification target rather than turning concept work into a giant workflow matrix.

## Suggested Commit Shape

- `feat(阶段26): harden generated route mockup handoff`
