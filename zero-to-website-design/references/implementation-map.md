# Implementation Map

Use this reference after design docs exist and before editing code.

Do not use implementation mapping as retroactive paperwork. If the intake output, visual source map, route docs, or milestone target are still missing, treat that as a blocker for broad implementation rather than something to patch later.

## Preconditions

Before broad code changes, confirm the project has:

- a compact intake output or equivalent assumption record
- a visual source map or equivalent authority record
- reference decomposition for binding design images
- design-system and implementation-plan docs or project equivalents
- page specs or route notes for touched core routes
- a stated milestone target and route-verification destination

## Mapping Steps

1. Identify route scope.
2. Break each binding mockup into layout regions.
3. Map regions to existing or new components.
4. Identify shared primitives.
5. Identify assets and data needed by each region.
6. Define responsive behavior.
7. For asset-controlled binding regions, read `resource-atomicity.md` and create a Resource-To-File Map before generation, sourcing, drawing, extraction, or local file creation.
8. Choose the asset strategy:
   - final owned assets
   - historical mock assets
   - local structural mock assets
   - generated assets
9. Define the fidelity budget for binding references.
10. Record generated UI asset prompts when assets are needed to match the reference.
11. Choose the smallest implementation order that produces a coherent site.
12. List files to edit.
13. Record milestone target, route owner, and replacement trigger for any temporary-binding asset.
14. State verification commands and browser QA routes.
15. Record screenshot comparison destination.
16. Record intentionally deferred routes or blockers that limit the current pass.

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
- Intake basis:
- Reference decomposition:
- Fidelity budget:
- Components:
- Assets:
- Resource-To-File Map:
- Generated UI asset prompts:
- Asset strategy:
- Data sources:
- Desktop behavior:
- Mobile behavior:
- Files to edit:
- Verification:
- Screenshot comparison destination:
- Known risks:
- Milestone target:
- Temporary route owners:
- Upgrade triggers:
- Deferred routes:
- Blockers:
```
