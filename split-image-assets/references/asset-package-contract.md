# Asset Package Contract

## Default Layout

```text
asset-package/
  source/
    source_original.png
  assets/
    main_object_transparent.png
    secondary_01_transparent.png
    secondary_group.png
    shadow_optional.png
    background_clean.png
  masks/
    mask_main.png
    mask_secondary_01.png
    mask_all_foreground.png
  previews/
    main_object_whitebg.png
    main_object_checkerboard.png
    overview_decomposition.png
    sprite_sheet_2x2.png
  metadata.json
  qa_report.md
```

Object counts vary. Prefer `main_object`, then `secondary_01`, `secondary_02`, and so on. Record the exact inventory in `metadata.json`.

## Metadata Fields

`metadata.json` must include:

- `schema_version`
- `package_name`
- `source.path`
- `source.width`
- `source.height`
- `objects`
- `previews`
- `qa.status`

Each object should include:

- `id`
- `role`: `main`, `secondary`, `group`, `background`, or `shadow`
- `asset_path`
- `mask_path` when a mask exists
- `bbox` when known
- `width`, `height`, `aspect_ratio`, and `area_ratio` when known
- `extraction_method`: `exact`, `ai-assisted`, `manual`, `estimated`, or `unknown`
- `confidence`: `high`, `medium`, or `low`
- `edge_complexity`: `hard`, `soft`, or `transparent-reflective`
- `manual_review_flags`

## Production Assets Versus Previews

Transparent object PNGs, masks, and cleaned backgrounds are production assets.

White-background previews, checkerboard previews, overview layouts, and 2x2 sprite sheets are inspection artifacts. They help review the package but do not replace the reusable assets.

