# Zero-To-Website Design V14 Metadata, Route-Data, And Feed Integrity Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: delivery-integrity hardening

## Goal

Tighten the package's metadata, route-data, and feed integrity contract so downstream website work cannot claim delivery readiness while slugs, rendered content, metadata, and exported feed outputs disagree.

The package already covers content readiness, route evidence, visual provenance, QA, and continuity. The remaining weak spot is the explicit consistency contract between route data, page output, metadata, and feed-like outputs.

## Why This Phase

`zero-to-website-design` already says:

- route generation should use the same data source as rendered pages
- slugs should be unique
- sitemap/RSS/robots should match exported or deployed routes when present
- metadata should use the approved brand

But these checks are still distributed across several references and templates rather than a single dedicated contract surface.

That creates room for a common failure mode:

- the visible page looks right
- the list/detail routes are present
- but metadata, feed output, or generated/static route sources drift apart

This phase turns that into an explicit contract so `Framework Ready` and `Visual Delivery Ready` cannot be claimed with hidden route/data inconsistencies.

## Target Outcome

After this phase, the package should make it natural to preserve:

- a route-data source of truth for every touched route family
- slug uniqueness and rendered route identity checks
- metadata ownership and output alignment
- sitemap/RSS/robots or equivalent feed output alignment when present
- explicit blockers when route/data/metadata mismatch exists

## Scope

In scope:

- harden `zero-to-website-design/references/implementation-map.md`
- harden `zero-to-website-design/references/route-acceptance.md`
- harden `zero-to-website-design/references/visual-qa-checklist.md`
- harden `zero-to-website-design/references/production-delivery.md`
- harden `zero-to-website-design/assets/templates/implementation-plan.md`
- harden `zero-to-website-design/assets/templates/qa-report.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new runtime scripts
- browser automation changes
- changing route evidence status names
- changing content-readiness rules
- changing visual provenance semantics

## Concrete Gaps To Close

### 1. Data-source integrity is only implied

The package mentions route generation and rendered content matching, but not a dedicated route-data integrity contract that names the source owner, route family, and output alignment expectations together.

### 2. Metadata and feed outputs can drift separately

Metadata, sitemap, RSS, and robots are currently checked, but the contract still leaves room for projects to treat them as a post-hoc checklist rather than a delivery surface with explicit ownership.

### 3. Route identity checks need sharper reporting

The route acceptance and QA templates should make it obvious when a route is blocked by slug duplication, data mismatch, or metadata mismatch, rather than burying those failures inside generic readiness language.

### 4. Delivery readiness should be explicitly bounded by route/data parity

A site should not be able to claim a stronger final state when route generation, rendered pages, metadata, and feed outputs are not aligned.

## Proposed Changes

### `references/implementation-map.md`

Add explicit mapping prompts for:

- route data source of truth
- metadata source of truth
- feed output source of truth
- slug uniqueness owner
- route-data mismatch blocker

### `references/route-acceptance.md`

Clarify that:

- route evidence should record data-source alignment
- slug collisions or route identity mismatches block readiness
- metadata and feed alignment are part of route acceptance when present

### `references/visual-qa-checklist.md`

Add checks for:

- route-data consistency
- metadata/final output consistency
- sitemap/RSS/robots consistency when those outputs exist

### `references/production-delivery.md`

Strengthen the final handoff to require:

- route-data source owner
- metadata owner
- feed/output alignment result
- explicit blocker when static/generated output diverges from rendered pages

### `assets/templates/implementation-plan.md`

Add fields for:

- data source of truth
- metadata source of truth
- feed/export source of truth
- route identity risk
- mismatch blocker

### `assets/templates/qa-report.md`

Add fields for:

- route-data integrity status
- metadata integrity status
- feed/output integrity status
- slug uniqueness or route identity issues
- blocker owner for route/data drift

### `docs/usage/zero-to-website-design.md`

Add a compact route-data integrity section that explains:

- route generation and rendered pages must come from the same source records
- metadata and feeds must match the rendered route set
- route identity drift blocks final delivery readiness

### Tests

Expand package tests so the repo proves:

- the new route-data / metadata / feed integrity wording exists
- implementation-plan and QA-report templates carry the new fields
- production-delivery language now binds route identity and output parity

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- route-data, metadata, and feed integrity are called out explicitly in package docs
- implementation-plan and QA-report templates record source-of-truth and blocker ownership
- route acceptance and production delivery clearly block mismatched route identity or feed output
- tests lock the new contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use metadata/route-data/feed integrity hardening as the V14 stage for `zero-to-website-design`.
- Rationale: After V13, the package still leaves route generation, metadata, and feed outputs as a distributed consistency concern. A dedicated contract is the clearest remaining way to stop hidden source drift from masquerading as delivery readiness.
- Risk: The contract may be heavy for very small static sites.
- Mitigation: Keep the new wording focused on source ownership and parity checks rather than inventing a bigger data architecture.

## Suggested Commit Shape

- `feat(阶段23): harden metadata route-data feed integrity`
