# Visual QA Checklist

Use this reference before signoff.

## Build First

Run the project's build, typecheck, or static export command before browser QA.

If dev server behavior differs from production export, QA the artifact that will actually ship and record the reason.

## Viewports

Minimum:

- desktop: `1440x900` or `1600x900`
- mobile: `390x844`

Add tablet or wide desktop when the design has unusual breakpoints.

## Route Matrix

Check:

- homepage
- primary listing/index route
- one representative detail route
- one representative category/filter/archive route
- any route with custom layout or risky interaction

Record an exception when a listed route type does not exist or is intentionally out of scope.

## Browser Checks

For each route:

- page loads without console-blocking errors
- `document.documentElement.scrollWidth <= document.documentElement.clientWidth`
- no incoherent overlap
- no clipped important text
- navigation links work
- primary action links work
- mobile menu opens and closes when present
- local images/assets load with no broken image indicators
- hover/focus states do not resize fixed layout controls

## Required Evidence Fields

For every route evidence row, record:

- route path
- route type
- source owner or visual reference
- reference screenshot path when a binding design controls the route
- implementation screenshot path
- side-by-side comparison path when a binding design controls the route
- page item fidelity audit path when a binding design controls the route
- desktop viewport checked
- mobile viewport checked
- screenshot path or QA note path
- console result
- overflow result
- navigation/link result
- local asset result
- mobile menu result when applicable
- readiness status
- fidelity status
- blocking failures
- blocking visual deviations
- unchecked design items
- blocked design items
- accepted gaps

Browser QA must cover both desktop and mobile for the route matrix unless an exception is recorded with a reason and risk.

## Screenshot Evidence

Save screenshots using names that include:

- route
- viewport
- date or pass name

Example:

```text
output/qa-screenshots/final-pass-YYYY-MM-DD/home-1600x900.png
```

Keep screenshot paths stable enough for another session to find and inspect them.

## Failure Classification

Classify every failed browser check as:

- `blocking-framework`: layout, overflow, broken route, broken navigation, broken primary action, missing local asset, or console-blocking error
- `blocking-visual`: mismatch against a binding reference, unresolved metadata issue, weak final asset quality, or unacknowledged temporary visual source
- `accepted-gap`: known and explicitly allowed for the current milestone
- `out-of-scope`: not included in this pass and not used to support readiness claims

Palette-only restyling is a blocking visual deviation when a binding design reference exists. If the page only copies colors, fonts, or rounded corners while missing layout geometry, component silhouettes, custom resources, or hierarchy, classify it as `blocking-visual`.

Full-page screenshot implementation is a blocking visual deviation when a binding design reference exists. If the page renders the whole selected design image as an `<img>`, background, canvas bitmap, or equivalent raster surface and adds transparent hotspots or invisible links, classify it as `blocking-visual` even when the screenshot looks identical. The route must be rebuilt as real text, DOM structure, controls, links, charts or diagrams, local assets, and responsive layout before `Visual Delivery Ready`.

Fix `blocking-framework` before claiming `Framework Ready`.

Fix or explicitly downgrade `blocking-visual` before claiming `Visual Delivery Ready`.

## Visual Gap Report

When working from reference images, report:

- what matches
- what remains different
- whether the gap is blocking or acceptable
- what would be needed for a closer pass

Never claim pixel fidelity when only structural similarity was checked.

## Design Fidelity Evidence

When a route has a binding reference image, also follow `design-fidelity-loop.md`.

The QA record must include:

- reference decomposition summary or link
- reference screenshot path
- implementation screenshot path
- side-by-side comparison path or comparison note
- page-by-page, item-by-item fidelity audit path
- difference summary
- blocking visual deviations
- unchecked or blocked design items
- accepted visual gaps
- next fix action or final fidelity status

Use this evidence during development, not only at the end. If the screenshot is still far from the design, or if any required audit item is `not-checked` or `blocked`, fix the route and capture a new implementation screenshot before claiming readiness.
