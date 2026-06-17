# Content Readiness

Use this reference when deciding whether placeholder, curated, generated-draft, or production content is acceptable for the current website milestone.

## Content Source Classes

Use explicit route-family content status labels:

- `production`: approved final content or the project's real source of truth
- `curated`: intentionally selected stand-in content that is realistic enough to validate layout and route structure
- `placeholder`: obviously temporary content used only to hold space or test module shape
- `generated-draft`: machine-written draft content that still needs human approval or replacement
- `mixed`: a route family that combines multiple source classes and must say which parts remain provisional

Do not leave route-family content status implicit.

## Route-Family Contract

For each route family or major route type, record:

- content source status
- source owner
- route family owner
- metadata owner
- whether the current pass is allowed to stay framework-first
- placeholder or draft replacement trigger
- what blocks stronger readiness claims

Examples of route families:

- homepage marketing sections
- post or article detail pages
- category or archive listings
- docs index and docs detail pages
- portfolio/project cards and project detail routes

## Framework-Ready Allowances

`Framework Ready` may still use `curated`, `placeholder`, `generated-draft`, or `mixed` content only when:

- the route structure is stable enough to validate layout and interactions
- placeholder policy is documented in the asset/data spec or equivalent docs
- the route family owner is named
- metadata framing is coherent enough to avoid misleading brand or taxonomy output
- any route-specific content blocker is visible in implementation, QA, or handoff docs

`Framework Ready` should not be claimed when:

- content structure is still too vague to validate layout
- route/detail pages still point at shared generic filler instead of route-specific shape
- placeholder brand, taxonomy, or IA labels actively contradict the approved direction
- content ownership is unknown

## Visual Delivery Ready Expectations

`Visual Delivery Ready` requires stronger content readiness than a framework milestone.

Before using a final delivery claim, verify:

- required route families are `production` or explicitly approved `curated`
- unresolved `placeholder` or `generated-draft` content is called out as a blocker unless the user explicitly accepts framework-only delivery
- metadata, slugs, taxonomies, and route generation match the rendered content source
- obsolete placeholder brand text is absent from active UI and metadata paths
- unresolved placeholder-brand drift is treated as a delivery blocker

Do not treat visual polish as enough to override unresolved content-source drift.

## Curated Versus Placeholder Guidance

Use `curated` when the stand-in content is realistic enough to test:

- card density
- title length
- excerpts or summaries
- detail-page hierarchy
- table, list, quote, or code-block behavior
- navigation labels

Use `placeholder` only when the content mainly reserves shape and spacing.

If `placeholder` content controls meaning-bearing UI such as:

- final headlines
- taxonomy labels
- CTA labels
- product claims
- author identity
- dates or prices

then document a replacement trigger before broad implementation continues.

## Generated-Draft Rules

`generated-draft` content may support layout exploration or framework delivery, but it does not count as approved factual or final editorial content by default.

When generated draft content is present, record:

- why a stronger source was not available yet
- who owns review or replacement
- whether the draft can appear in screenshots for the current milestone
- what must happen before final delivery

Do not use generated draft content as implied factual approval.

## Metadata And Route/Data Integrity

Check:

- route generation and rendered detail routes use the same source records
- list and detail routes agree on slug, title, and summary identity
- metadata owner is named
- metadata source status matches route content status
- sitemap, RSS, and taxonomy outputs align with the chosen content source when present
- placeholder or obsolete brand text is removed from active metadata paths before final delivery

## Readiness Blockers

Record blockers when any of these remain true:

- route family owner is unknown
- placeholder replacement trigger is missing
- metadata source is undefined
- detail pages still render shared generic content instead of route-specific content
- taxonomy or archive structure does not match the rendered route set
- content source status is still mixed but the unresolved parts are not named

These blockers may still allow `Framework Ready`, but they must limit stronger delivery claims until resolved.

## Reporting Expectations

Final reports or handoffs should say:

- content source status by touched route family
- whether framework-first delivery still relies on curated, placeholder, or generated-draft content
- metadata and route/data integrity result
- blocker owner and replacement trigger for unresolved content issues
- whether the current pass stops at `Framework Ready` or can claim `Visual Delivery Ready`
