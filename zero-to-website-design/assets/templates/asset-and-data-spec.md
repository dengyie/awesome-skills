# Asset And Data Spec

## Content Sources

| Source | Purpose | Owner | Notes |
| --- | --- | --- | --- |

## Placeholder Policy

- Placeholder content allowed:
- Must be replaced before production:
- Safe fake data rules:

## Data Integrity

- Unique identifiers:
- Route generation:
- Metadata generation:
- Sitemap/RSS:

## Visual Assets

| Asset | Source Method | Authority Status | Used By | Ownership Scope | Replacement Trigger | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Resource Decomposition

| Reference Region | Resource Unit | Unit Type | File Path | Owner Component | Reuse Scope | Split Reason | Must Stay Separate From | May Compose With | Text Policy | Edit Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Split visual resources by edit, reuse, responsive, interaction, text, licensing, and replacement boundaries. Do not bake independent cards, icons, labels, controls, ornaments, panels, textures, or diagram layers into one raster just because they are adjacent in a reference.

## Composite Assets

| Parent Asset | Child Pieces Included | Why Composite Is Allowed | Must Stay Separate | Text Policy | Edit Boundary | Replacement Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Composite assets must represent one semantic illustration, product panel, texture plate, or diagram-art unit. If children need independent movement, reuse, localization, source handling, replacement, or interaction, split them into separate resources and compose them in DOM/CSS.

## Asset Rules

- External assets:
- Local assets:
- Generated assets:
- Icons:
- Fonts:
- Temporary visual scope:
- Resource atomicity:
- Spritesheets:

## Verification

- [ ] No broken images
- [ ] No unapproved hotlinks
- [ ] Asset paths work in production
- [ ] Metadata/feed data matches rendered routes
- [ ] Replacement triggers are recorded for temporary or generated route owners
- [ ] Resource-To-File Map exists for binding-route visual assets
- [ ] No asset remains `blocked-maintainability` because it combines independent resources
