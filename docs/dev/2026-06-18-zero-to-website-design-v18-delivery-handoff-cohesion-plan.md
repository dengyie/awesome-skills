# Zero-To-Website Design V18 Delivery Handoff Cohesion Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: delivery-artifact hardening

## Goal

Tighten the package's delivery and continuation artifacts so the final report, QA report, and workstream preserve the stronger route, asset, and generated-route authority state already required by the earlier workflow stages.

The package already has stronger contracts for:

- pre-code document gates
- route-level specs
- content/data readiness
- metadata/feed integrity
- asset authority and upgrade queues
- generated route-mockup inheritance and escalation

But the final delivery-facing artifacts still summarize some of that richer state too lightly.

## Why This Phase

`zero-to-website-design` now expects projects to preserve:

- route evidence status
- temporary-binding ownership
- upgrade queues
- generated route-mockup coverage
- inherited authority from selected concepts
- escalation targets and next verification targets

Yet the main delivery-facing artifacts still under-record:

- whether a reported source reference is inherited from a selected concept or route-specific
- whether unresolved generated route coverage still limits readiness
- which escalation target remains active at handoff time
- whether the weakest required route is weak because of visual fidelity, route-data, or incomplete route-mockup expansion

That means the implementation-side contracts are stronger than the final delivery and continuation record. Another session could still reopen the project and reconstruct too much of the actual readiness story from scattered docs.

## Target Outcome

After this phase, the package should make it natural to preserve in final delivery artifacts:

- route-mockup coverage status for generated or temporary route owners
- inherited authority versus route-specific authority
- escalation target still active at handoff time
- strongest and weakest route evidence reasons
- next continuation target when final delivery is not yet claimed

## Scope

In scope:

- harden `zero-to-website-design/references/production-delivery.md`
- harden `zero-to-website-design/assets/templates/qa-report.md`
- harden `zero-to-website-design/assets/templates/website-workstream.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new scripts
- route evidence status renames
- changes to concept-generation authority rules themselves
- new templates

## Concrete Gaps To Close

### 1. Final handoff still under-reports generated route authority detail

The final delivery format mentions temporary-binding ownership and route evidence, but it still does not strongly require generated route-mockup coverage, inherited authority, or active escalation targets.

### 2. QA report lags behind the newer authority contract

The QA report already tracks route evidence and continuation ownership, but it does not make it natural to preserve route-mockup coverage status, inherited authority, or escalation target for generated route owners.

### 3. Workstream status still compresses too much of the final readiness story

The website workstream names route slice, visual source status, and weakest route evidence status, but it can still lose why the weakest route remains weak when generated or temporary route owners are involved.

## Proposed Changes

### `references/production-delivery.md`

Strengthen final handoff expectations so the report includes:

- generated route-mockup coverage status when applicable
- inherited authority versus route-specific authority for generated route owners
- active escalation target for unresolved provisional route owners
- why the weakest required route still limits the overall claim

### `assets/templates/qa-report.md`

Add fields for:

- generated route-mockup coverage status
- inherited authority notes
- active escalation target
- weakest-route limiting reason

### `assets/templates/website-workstream.md`

Add fields for:

- weakest route limiting reason
- generated route-mockup coverage status
- inherited authority summary
- active escalation target

### `docs/usage/zero-to-website-design.md`

Add a short delivery-handoff section that explains final artifacts should preserve the same authority and route-coverage detail the earlier design and mockup artifacts already require.

### Tests

Expand package tests so the repo proves:

- production delivery wording now includes generated route coverage and escalation reporting
- QA report and website workstream templates carry the stronger continuation fields
- usage docs expose the stronger delivery-handoff expectation

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- production delivery wording preserves stronger generated and temporary authority state
- QA report and website workstream templates carry the new continuation and limiting-reason fields
- usage docs expose the stronger delivery-handoff expectation
- tests lock the contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use delivery handoff cohesion as the V18 stage for `zero-to-website-design`.
- Rationale: The package's earlier workflow stages are now stricter than the final delivery-facing artifacts. Tightening the reporting and continuation layer keeps the end of the workflow from being the loosest part.
- Risk: The delivery artifacts could become too heavy for small sites.
- Mitigation: Keep the new fields focused on authority continuity, weakest-route reasoning, and next-step ownership rather than introducing a large reporting matrix.

## Suggested Commit Shape

- `feat(阶段27): harden delivery handoff cohesion`
