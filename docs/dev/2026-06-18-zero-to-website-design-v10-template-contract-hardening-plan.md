# Zero-To-Website Design V10 Template Contract Hardening Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: delivery-template hardening

## Goal

Align the core shipped templates with the stronger provenance, route-readiness, QA-evidence, and handoff contract already present in the V6-V9 workflow references.

The package is now much stricter about:

- historical and generated visual authority
- `temporary-binding` ownership and replacement triggers
- route readiness and browser QA evidence

The remaining weak spot is that several core templates still do not give another session a natural place to record those requirements.

## Why This Phase

A workflow is only as strong as the artifacts it produces.

Right now, the package references and usage docs can ask for:

- route owner and replacement trigger
- route evidence rows and readiness status
- asset-source method and delivery risk
- handoff-sensitive gaps

But the shipped templates for implementation, route specs, assets/data, and design system still leave some of that structure implicit. That creates drift exactly where downstream projects copy the workflow into local docs.

## Target Outcome

After this phase, the package templates should make it natural to record:

- milestone and route readiness state
- source authority and route ownership
- QA evidence expectations
- asset replacement or upgrade triggers
- final delivery blockers versus accepted gaps
- handoff-sensitive follow-up state

## Scope

In scope:

- harden `zero-to-website-design/assets/templates/implementation-plan.md`
- harden `zero-to-website-design/assets/templates/page-spec.md`
- harden `zero-to-website-design/assets/templates/asset-and-data-spec.md`
- harden `zero-to-website-design/assets/templates/design-system-master.md`
- align `zero-to-website-design/tests/test_skill_package.py`
- update project memory for the new stage

Out of scope:

- adding new templates
- changing reference-file authority rules
- adding scripts or automation
- changing unrelated packages

## Concrete Gaps To Close

### 1. Implementation planning does not ask for route evidence ownership

The implementation plan template includes QA and milestone sections, but it does not explicitly ask for route evidence output paths, weakest claimed status, or route-owner level delivery risk.

### 2. Page specs are not yet explicit enough about readiness and evidence

The route-spec template should have a stronger place for route type, source owner, route status, viewport coverage, and handoff-sensitive gaps.

### 3. Asset/data specs under-record replacement and delivery risk

Asset/data planning should make it easier to record source method, current authority, replacement trigger, and whether assets still affect route composition.

### 4. Design-system docs under-record milestone and binding-source scope

The design-system template should make it easy to record binding references, milestone target, rejected scope, and final readiness gate language that matches the strengthened workflow.

## Proposed Changes

### `assets/templates/implementation-plan.md`

Add fields for:

- route evidence destination
- route-owner risk
- weakest expected route status
- accepted-gap policy

### `assets/templates/page-spec.md`

Add fields for:

- route type
- source owner
- viewport evidence target
- current route status
- blocking failures versus accepted gaps

### `assets/templates/asset-and-data-spec.md`

Add fields for:

- source method
- authority status
- replacement trigger
- route-composition versus slot/texture ownership

### `assets/templates/design-system-master.md`

Add fields for:

- milestone target
- binding-route versus temporary-binding references
- temporary visual scope
- final route-readiness gate

### Tests

Expand package tests so the repo proves the shipped templates can hold:

- route evidence and readiness data
- stronger asset provenance and replacement tracking
- milestone and handoff-sensitive delivery state

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- the four core templates reflect the stronger V6-V9 contract
- tests lock the new template fields
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use template-contract hardening as V10 instead of opening another reference-only pass.
- Rationale: The references are already stricter than the templates that downstream projects copy into their repos. Tightening those templates has higher leverage than further prose refinement elsewhere.
- Risk: More template fields can feel heavier during small projects.
- Mitigation: Keep fields compact and strongly scoped to delivery-critical information only.

## Suggested Commit Shape

- `feat(阶段18): harden delivery templates`
