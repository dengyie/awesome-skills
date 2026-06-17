# Visual Provenance

Use this reference before treating any image, screenshot, Figma export, generated mockup, or live-site capture as authoritative.

## Status Values

- `exploratory`: helps ideation, does not control implementation
- `candidate`: available for user selection
- `approved-direction`: user selected this direction, but route-specific authority may still be pending
- `binding-route`: implementation must match this route-level reference
- `temporary-binding`: acceptable for the current framework or mock pass, but expected to be upgraded later
- `obsolete`: retained for history but not used

## Source Methods

Record one:

- `user-upload`
- `imagegen`
- `figma-export`
- `live-screenshot`
- `manual-design`
- `existing-project-mockup`
- `existing-project-screenshot`
- `other`

## Visual Source Map Template

```md
| Asset | Source Method | Date | Status | Controls | Route Family | Viewport | Authority Reason | Milestone Supported | Readiness Limiter | Upgrade Queue | Next Verification Target | Blocker Owner | Replacement Trigger | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| output/design/homepage.png | imagegen | YYYY-MM-DD | binding-route | `/` route composition | marketing shell | desktop+mobile | User selected concept A for the shipped homepage structure | Visual Delivery Ready | none | homepage-final-pass | verify final desktop/mobile QA row | design owner | Replace only if a newer route mockup is approved | User selected concept A |
```

## Authority Rules

- A live site reference can inspire behavior, but it is not binding unless the user says to match it.
- A generated concept image is not route-binding until selected and mapped to a route.
- A route mockup overrides a broad concept image for that route.
- A design-system doc overrides older chat descriptions when the user approved the doc.
- A `temporary-binding` image can drive framework delivery, but it must be called out in final reports and upgrade notes.
- When two binding references conflict, stop and either pick the route-specific reference or ask the user.

## Ownership Scope

When recording `Controls`, make the ownership scope explicit:

- whole route composition
- section composition
- illustration slot shape
- palette or texture only

Do not collapse all of these into a vague "visual reference" label. A temporary image that only informs texture is materially different from one that owns the route layout.

## Required Fields For Binding Images

Each binding image must have:

- file path or URL
- source method
- date
- route or section ownership
- route family or active route slice ownership
- authority reason
- milestone supported
- readiness limiter
- upgrade queue when the asset is still provisional
- next verification target when the asset still needs QA or replacement
- blocker owner when the asset still limits readiness
- replacement trigger
- viewport represented
- approval status
- known limitations

For `temporary-binding` images, also record whether the asset is strong enough for:

- `Framework Ready`
- `Visual Delivery Ready`
- support only, not direct ownership

If multiple `temporary-binding` assets are moving through the same replacement plan, record them as one active upgrade queue instead of leaving the relationship implicit.

## Known Limitation Examples

- generated text is illustrative only
- desktop frame exists but mobile must be inferred
- mobile frame exists but intermediate tablet widths are not specified
- image shows mood but not exact content hierarchy
- screenshot includes browser chrome or non-site UI
