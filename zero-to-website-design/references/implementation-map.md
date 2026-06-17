# Implementation Map

Use this reference after design docs exist and before editing code.

## Mapping Steps

1. Identify route scope.
2. Break each binding mockup into layout regions.
3. Map regions to existing or new components.
4. Identify shared primitives.
5. Identify assets and data needed by each region.
6. Define responsive behavior.
7. Choose the asset strategy:
   - final owned assets
   - historical mock assets
   - local structural mock assets
   - generated assets
8. Choose the smallest implementation order that produces a coherent site.
9. List files to edit.
10. State verification commands and browser QA routes.

## Component Mapping Prompts

For each route, decide:

- page shell or frame
- header/nav
- hero or top content area
- listing/card system
- filters/categories/search
- detail/content body
- footer
- decorative/brand assets
- empty/loading/error states when relevant

## Implementation Order

Prefer:

1. global tokens and layout shell
2. shared components
3. homepage
4. primary listing/index route
5. detail route
6. category/filter/archive routes
7. metadata and feeds
8. visual polish and QA fixes

## Guardrails

- Follow the existing framework and project conventions.
- Keep edits scoped to the current phase.
- Avoid unrelated refactors.
- Do not delete files without explicit confirmation.
- Keep static export/deploy constraints visible.
- Replace split or duplicated data sources before final delivery.
- Name whether the current target is `Framework Ready` or `Visual Delivery Ready`.

## Implementation Map Output

Write a compact map before code:

```md
## Implementation Map
- Routes:
- Binding references:
- Components:
- Assets:
- Asset strategy:
- Data sources:
- Desktop behavior:
- Mobile behavior:
- Files to edit:
- Verification:
- Known risks:
- Milestone target:
```
