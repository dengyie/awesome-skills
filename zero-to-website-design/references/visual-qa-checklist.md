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

## Screenshot Evidence

Save screenshots using names that include:

- route
- viewport
- date or pass name

Example:

```text
output/qa-screenshots/final-pass-YYYY-MM-DD/home-1600x900.png
```

## Visual Gap Report

When working from reference images, report:

- what matches
- what remains different
- whether the gap is blocking or acceptable
- what would be needed for a closer pass

Never claim pixel fidelity when only structural similarity was checked.

