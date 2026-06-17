# Zero-To-Website Design V13 Content And Data Readiness Contract Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: delivery-contract hardening

## Goal

Tighten the package's content and data readiness contract so framework-first delivery can safely use placeholder or curated content without letting final delivery claims drift past unresolved content, metadata, or source-of-truth gaps.

The package already has strong contracts for visual source authority, pre-code docs, route evidence, delivery templates, and continuity. The remaining soft spot is that content/data readiness still lives across scattered wording instead of a single explicit reference.

## Why This Phase

`zero-to-website-design` explicitly claims that a complete website pass checks content/data sources in addition to visuals and implementation.

Right now the package already mentions:

- placeholder versus production content
- route generation and rendered data should match
- framework-first delivery may stop before final content polish

But it still under-specifies:

- when placeholder or curated content is acceptable
- what must be recorded before placeholder content is allowed to control a route
- when data/content gaps block `Framework Ready` versus only `Visual Delivery Ready`
- what minimum metadata/content integrity checks must appear in docs and handoff

That gap makes it easier for downstream projects to ship visually strong work while silently carrying content-source drift, route/data mismatches, or stale placeholder brand text.

## Target Outcome

After this phase, the package should make it natural to preserve:

- the chosen content source status for each route family
- placeholder versus production content policy for the current milestone
- route/data ownership and replacement trigger when temporary content stands in
- metadata and route-generation integrity checks
- content blockers that prevent stronger delivery claims

## Scope

In scope:

- add `zero-to-website-design/references/content-readiness.md`
- align `zero-to-website-design/SKILL.md`
- align `zero-to-website-design/references/design-system-docs.md`
- align `zero-to-website-design/references/framework-first-delivery.md`
- align `zero-to-website-design/references/production-delivery.md`
- harden `zero-to-website-design/assets/templates/asset-and-data-spec.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new scripts or automation
- changing route-evidence status names
- changing visual provenance semantics
- adding new templates beyond the new reference
- modifying unrelated packages

## Concrete Gaps To Close

### 1. Content readiness rules are distributed instead of explicit

The package mentions content strategy in intake, design docs, implementation maps, and production delivery, but there is no dedicated reference that a website-delivery pass can load when deciding whether placeholder or curated content is acceptable.

### 2. Framework-first content allowances are not sharp enough

The current workflow says placeholder or curated content can be used, but it does not sharply define what must be true before placeholder content is acceptable for a route at the current milestone.

### 3. Data and metadata integrity checks are lighter than the visual contract

The production-delivery reference checks some metadata and route-generation conditions, but the asset/data template still under-specifies route family ownership, placeholder retirement triggers, and delivery blockers tied to content.

### 4. Final delivery claims can still drift past content gaps

The package should make it explicit that unresolved placeholder brand text, mismatched route/detail data, or undefined content ownership can limit readiness claims even when the UI looks complete.

## Proposed Changes

### `references/content-readiness.md`

Add a dedicated reference covering:

- content-source classes such as production, curated, placeholder, generated-draft, and mixed
- when each class is acceptable for `Framework Ready` versus `Visual Delivery Ready`
- route-family ownership expectations
- placeholder replacement triggers
- metadata and route/data integrity checks
- blockers that limit final delivery claims

### `SKILL.md`

Clarify that:

- content/data readiness is a first-class gate, not a side note
- framework-first delivery can use placeholder or curated content only when the route policy is documented
- final delivery cannot overclaim past unresolved content-source drift

### `references/design-system-docs.md`

Make the design-doc gate more explicit about:

- content-source status by route family
- placeholder replacement conditions
- metadata ownership and integrity expectations

### `references/framework-first-delivery.md`

Clarify which content gaps are acceptable at framework milestone and which still block a valid framework-ready claim.

### `references/production-delivery.md`

Strengthen final checks for:

- unresolved placeholder brand or taxonomy drift
- route/detail content mismatch
- undefined source ownership
- stronger claim limits when content/data blockers remain

### `assets/templates/asset-and-data-spec.md`

Add fields for:

- content source status
- route family owner
- placeholder replacement trigger
- metadata owner
- framework-ready blocker
- final-delivery blocker

### `docs/usage/zero-to-website-design.md`

Add a compact content-readiness section that explains:

- when placeholder or curated content is acceptable
- what must be documented before broad implementation continues
- how content blockers affect final readiness claims

### Tests

Expand package tests so the repo proves:

- the new content-readiness reference exists and is routed by the skill
- content-source classes and milestone rules are documented
- asset/data templates and delivery docs encode the stronger content/data contract

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- a dedicated content-readiness reference exists
- skill routing and usage docs point to the new reference when content/data readiness matters
- design-doc, framework-first, production-delivery, and asset/data artifacts align around placeholder policy and content/data blockers
- tests lock the new contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use content-and-data readiness hardening as the V13 stage for `zero-to-website-design`.
- Rationale: The current package already makes visual, implementation, QA, and continuity state much stricter. The highest-leverage remaining gap is the content/data contract that decides when framework-first content is acceptable and when delivery claims must stop.
- Risk: The package could become too heavy for small static sites.
- Mitigation: Keep the new contract focused on route-family ownership, placeholder policy, and readiness blockers rather than introducing a large data-model schema.

## Suggested Commit Shape

- `feat(阶段22): harden content readiness contract`
