# Zero-To-Website Design V15 Page Spec Contract Hardening Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: route-contract hardening

## Goal

Tighten the package's page-spec contract so each touched core route can act as a compact source of truth for route purpose, route identity, content/data requirements, metadata expectations, QA evidence, and known gaps.

The package already has stronger global delivery contracts for provenance, QA, content readiness, continuity, and metadata/data integrity. The remaining soft spot is that the route-level page spec still under-records several of those requirements.

## Why This Phase

`zero-to-website-design` treats route/page specs as part of the required pre-code artifact chain.

Right now `page-spec.md` covers:

- purpose
- route identity
- delivery state
- layout
- components
- content/data
- interactions
- QA evidence
- known gaps

But it still under-specifies:

- route-data and metadata source-of-truth fields
- feed/output relevance when applicable
- route-specific blocker ownership
- explicit route-data / metadata integrity status
- route-level handoff-sensitive continuity when a page family is the blocker

That leaves room for a project to have strong global docs while the route-level source of truth is still too vague to resume or verify a specific page without rereading multiple artifacts.

## Target Outcome

After this phase, the package should make it natural for each core route spec to preserve:

- route identity and route-data source of truth
- metadata source and output expectations
- required content fields and placeholder policy
- integrity status and blocker owner for the route
- route-specific QA evidence destination
- route-level known gaps and handoff sensitivity

## Scope

In scope:

- harden `zero-to-website-design/references/design-system-docs.md`
- harden `zero-to-website-design/references/implementation-map.md`
- harden `zero-to-website-design/assets/templates/page-spec.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new scripts
- changing global route evidence status names
- changing content-readiness or metadata-integrity semantics already established
- adding new templates

## Concrete Gaps To Close

### 1. Page specs do not yet fully mirror the stronger global contract

The page spec still lacks dedicated fields for route-data source, metadata source, route integrity status, and blocker ownership, even though those are now part of the broader workflow contract.

### 2. Route-level blockers can still be too diffuse

When one page family is the blocker, the current page spec format still leaves too much of that reasoning in QA reports or workstreams instead of the route doc itself.

### 3. Handoff-sensitive route state is still light

The package's continuity contract is stronger now, but the per-route page spec does not explicitly name whether the route itself is handoff-sensitive or what another session must preserve to resume that route.

## Proposed Changes

### `references/design-system-docs.md`

Clarify that page specs should define:

- route-data source of truth
- metadata source of truth
- route integrity expectations
- route blocker owner when the route is not ready

### `references/implementation-map.md`

Clarify that implementation mapping should point to the page spec as the route-level source of truth for:

- route-data source
- metadata source
- route-specific blockers
- QA evidence destination

### `assets/templates/page-spec.md`

Add fields for:

- route-data source of truth
- metadata source of truth
- feed/output relevance
- route-data and metadata integrity status
- blocker owner
- unblock condition
- handoff-sensitive route context

### `docs/usage/zero-to-website-design.md`

Add a short route-spec section that explains a route doc should be enough for another session to understand what the page is, what data and metadata power it, how it is verified, and what still blocks it.

### Tests

Expand package tests so the repo proves:

- page-spec contract now includes route-data, metadata, blocker, and handoff-sensitive fields
- design-system and implementation references explicitly point page specs at the stronger route-level contract
- usage docs expose route-spec expectations

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- page-spec template reflects the stronger route-level contract
- design-system and implementation references route work through the stronger page spec
- usage docs expose route-spec expectations
- tests lock the new contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use page-spec contract hardening as the V15 stage for `zero-to-website-design`.
- Rationale: The package's global contracts are now strong, but the route-level spec is still slightly behind. Hardening page specs is the most direct way to keep the route as a resumable, auditable unit of work.
- Risk: The page spec could become too heavy for tiny one-page sites.
- Mitigation: Keep the new fields focused on route truth, blockers, and verification rather than turning the route doc into a giant checklist.

## Suggested Commit Shape

- `feat(阶段24): harden page spec contract`
