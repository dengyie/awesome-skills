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
- maintainability risks

Fix confirmed issues before delivery.

## Data And Metadata

Check:

- route generation uses the same data source as rendered pages
- detail pages render the selected item, not shared placeholder content
- slugs are unique
- sitemap/RSS/robots match exported or deployed routes when present
- metadata uses the approved brand
- obsolete placeholder brand names are absent from active UI paths

## Asset Delivery

Check:

- no broken local assets
- no unapproved hotlinked images
- generated assets are stored in the project when required
- asset paths work in the target deployment base path
- large assets are justified
- temporary-binding assets are acknowledged in the final report
- framework-first versus final-content status is clearly stated

## Final Handoff Format

Report:

- routes touched
- source references used
- design docs created or updated
- files changed
- build/test result
- desktop and mobile QA result
- production review result
- framework-ready versus visual-delivery-ready status
- known gaps
- deployment or PR link when applicable
