# Zero-To-Website Design V9 QA Evidence Contract Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: route acceptance and visual QA evidence hardening

## Goal

Harden the route acceptance and visual QA layer so the package requires durable evidence before claiming a route or website pass is ready.

After V6 through V8, the package has stronger rules for:

- historical and repo-owned visual sources
- provenance and temporary-binding ownership
- generated-image authority escalation

The remaining weak layer is proof. `route-acceptance.md` and `visual-qa-checklist.md` contain useful checks, but they do not yet make the acceptance record strict enough to prove what was tested, what passed, what failed, and what status can be claimed.

## Why This Phase

In real website work, the most expensive drift happens when an implementation is "visually close" but the final report cannot prove:

- which routes were checked
- which viewport evidence exists
- which failures were fixed or explicitly accepted
- whether a route is only `Framework Ready` or actually `Visual Delivery Ready`
- whether temporary assets still control route composition

This phase should turn QA from a loose checklist into an evidence contract.

## Target Outcome

When a route reaches final reporting, the package should make it obvious:

- what route and viewport matrix was tested
- where screenshots or QA notes were saved
- which checks are required before `Framework Ready`
- which additional checks are required before `Visual Delivery Ready`
- how failures are classified and handled
- how temporary-binding gaps affect the final status

## Scope

In scope:

- harden `zero-to-website-design/references/route-acceptance.md`
- harden `zero-to-website-design/references/visual-qa-checklist.md`
- align `zero-to-website-design/references/production-delivery.md`
- align the existing `zero-to-website-design/assets/templates/qa-report.md` scaffold with the stronger QA evidence contract
- align `zero-to-website-design/SKILL.md` and `docs/usage/zero-to-website-design.md` if needed
- expand regression tests for the QA evidence contract
- update project memory for the new stage

Out of scope:

- adding browser automation scripts
- changing the provenance status names
- changing generated-image authority rules
- changing unrelated packages

## Concrete Gaps To Close

### 1. Route acceptance does not require an evidence row

The package lists checks but does not require a compact record that ties route, viewport, source owner, status, screenshot path, and known gaps together.

### 2. Failure handling is too implicit

The current checklist says what to check, but does not say how to classify a failed check or how it affects `Framework Ready` versus `Visual Delivery Ready`.

### 3. Final handoff can overclaim readiness

The delivery reference asks for QA results, but it should explicitly require the final status to follow the recorded route evidence rather than broad narrative confidence.

## Proposed Changes

### `references/route-acceptance.md`

Add:

- a route acceptance evidence row format
- status values for `not-checked`, `blocked`, `framework-ready`, and `visual-delivery-ready`
- a rule that every touched core route needs a recorded status
- stricter guidance that failed layout, link, asset, or overflow checks block `Framework Ready`
- stricter guidance that unresolved fidelity, metadata, and temporary-asset gaps block `Visual Delivery Ready` unless explicitly accepted as post-pass gaps

### `references/visual-qa-checklist.md`

Add:

- required QA evidence fields
- failure classification
- screenshot and console evidence expectations
- a rule that browser QA must cover both desktop and mobile for the route matrix unless an exception is recorded

### `references/production-delivery.md`

Add:

- final handoff must summarize route evidence status
- readiness claims must match the lowest recorded route status
- production review should inspect missing or contradictory QA evidence

### `assets/templates/qa-report.md`

Update the scaffold so another session can actually record:

- route evidence rows
- route status
- source owner
- blocking failures
- accepted gaps
- final overall readiness claim

### Tests

Expand package tests so the repo proves:

- route acceptance includes an evidence contract
- visual QA includes failure classification and viewport evidence requirements
- production delivery cannot claim readiness without route evidence
- the shipped QA report template can capture the stricter evidence contract
- public usage docs mention route evidence and readiness status

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- route evidence rows are documented
- viewport, screenshot, console, link, asset, overflow, and gap evidence are required where relevant
- failed checks have explicit readiness impact
- final delivery claims are tied to recorded route evidence
- tests lock the stricter contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use QA evidence contract hardening as V9 instead of adding another source-provenance pass.
- Rationale: Source authority is now much stronger after V6-V8. The next production risk is overclaiming readiness without browser evidence that proves route and viewport coverage.
- Risk: This adds more reporting burden for small sites.
- Mitigation: Keep evidence rows compact and allow recorded exceptions when a route or viewport is genuinely out of scope.

## Suggested Commit Shape

- `feat(阶段17): harden qa evidence contract`
