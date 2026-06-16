# Visual Provenance

Use this reference before treating any image, screenshot, Figma export, generated mockup, or live-site capture as authoritative.

## Status Values

- `exploratory`: helps ideation, does not control implementation
- `candidate`: available for user selection
- `approved`: user selected this direction
- `binding`: implementation must match this reference
- `obsolete`: retained for history but not used

## Source Methods

Record one:

- `user-upload`
- `imagegen`
- `figma-export`
- `live-screenshot`
- `manual-design`
- `existing-project-screenshot`
- `other`

## Visual Source Map Template

```md
| Asset | Source Method | Date | Status | Controls | Viewport | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| output/design/homepage.png | imagegen | YYYY-MM-DD | binding | `/` | desktop+mobile | User selected concept A |
```

## Authority Rules

- A live site reference can inspire behavior, but it is not binding unless the user says to match it.
- A generated concept image is not binding until selected and mapped to a route.
- A route mockup overrides a broad concept image for that route.
- A design-system doc overrides older chat descriptions when the user approved the doc.
- When two binding references conflict, stop and either pick the route-specific reference or ask the user.

## Required Fields For Binding Images

Each binding image must have:

- file path or URL
- source method
- date
- route or section ownership
- viewport represented
- approval status
- known limitations

## Known Limitation Examples

- generated text is illustrative only
- desktop frame exists but mobile must be inferred
- mobile frame exists but intermediate tablet widths are not specified
- image shows mood but not exact content hierarchy
- screenshot includes browser chrome or non-site UI

