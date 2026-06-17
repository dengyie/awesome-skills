# Production Delivery

Use this reference before final handoff, deploy, PR, or publishing.

## Review Gate

Use a production review workflow when available. Review for:

- correctness
- source-of-truth drift
- duplicated data
- static route/export mismatch
- broken metadata
- accessibility regressions
- missing tests or QA evidence
- missing route evidence rows
- contradictory readiness claims
- maintainability risks

Fix confirmed issues before delivery.

## Data And Metadata

Check:

- touched route families have an explicit content source status
- route-family owner and metadata owner are defined
- route generation uses the same data source as rendered pages
- route-data source of truth is named for touched route families
- detail pages render the selected item, not shared placeholder content
- slugs are unique
- sitemap/RSS/robots match exported or deployed routes when present
- metadata uses the approved brand
- obsolete placeholder brand names are absent from active UI paths
- placeholder or generated-draft content still in use has an explicit replacement trigger

## Asset Delivery

Check:

- no broken local assets
- no unapproved hotlinked images
- generated assets are stored in the project when required
- asset paths work in the target deployment base path
- large assets are justified
- temporary-binding assets are acknowledged in the final report
- temporary-binding assets say whether they still control route composition, slot shape, or only texture/palette
- framework-first versus final-content status is clearly stated

## Final Handoff Format

Report:

- routes touched
- content source status for each touched route family
- route-data source owner
- route evidence status for each touched core route
- source references used
- design docs created or updated
- files changed
- build/test result
- desktop and mobile QA result
- production review result
- framework-ready versus visual-delivery-ready status
- metadata and route/data integrity result
- sitemap/RSS/robots or equivalent feed/output integrity result
- temporary-binding ownership and upgrade triggers
- known gaps
- deployment or PR link when applicable

## Readiness Claim Rules

- The overall website status cannot be stronger than the weakest required route evidence status.
- A route with `not-checked` or `blocked` evidence cannot support a final ready claim.
- A site can be `Framework Ready` while still carrying visual gaps only when those gaps are recorded as accepted gaps.
- A site can be `Framework Ready` while still carrying content gaps only when those route-family blockers, owners, and replacement triggers are explicitly recorded.
- A site can be `Visual Delivery Ready` only when every required route is `visual-delivery-ready` or explicitly out of scope.
- A site with unresolved placeholder-brand drift, undefined content ownership, or route/detail content mismatch cannot claim final delivery readiness.
- A site with unresolved slug collisions, route-data drift, or feed/output mismatch cannot claim final delivery readiness.
- Final reports must not summarize QA as "passed" when route evidence contains unresolved blocking failures.
