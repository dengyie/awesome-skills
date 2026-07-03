# UI Atomic Split Planning

Use this reference before extracting complex UI screenshots, dashboards, app mockups, badges, icon tiles, or dense interface panels.

The question is not only "can the pixels be cut out"; it is "what should become reusable". Build a semantic split plan before running a segmenter or importing upstream assets.

Default bias: editability first. Ordinary text-like UI content should usually route to `rebuild_downstream`. Only fidelity-critical visual elements should route to raster extraction.

Classify each target object before extraction or repair:

- `ui-carrier`: tile, badge, chip, button body, panel capsule
- `ui-glyph`: hard-edge icon, symbol, check mark, status glyph, nav icon
- `carrier-glyph-pair`: icon-in-tile, symbol-on-button, badge-plus-glyph
- `soft-edge-logo-brand-mark`: softer logo edges or glow-driven brand marks
- `outlined-illustration-logo`: black-outline or strong-stroke illustration marks
- `flat-support-plate`: support rectangle or reconstructed plate
- `photo-object-matte`: matte-like non-UI object

## Planning Layers

List expected UI layers in this order:

- structural plates: page background, panels, cards, sidebars, bars, clean plates
- carrier tiles: button bodies, icon tiles, badges, chips, status capsules
- glyphs: icons, symbols, check marks, row glyphs, arrows, small pictograms
- text labels: labels, numbers, captions, button text, dense copy
- status dots: lights, pins, indicators, selection markers
- chart marks: bars, lines, points, axes, labels, legends
- controls: checkboxes, toggles, sliders, handles, tabs, menus
- shadows/glows: support effects that may be grouped or rebuilt downstream
- grouped convenience layers: optional combined layers for quick preview or simple reuse

## Required Plan Fields

For each planned layer, record:

- `layer_id`
- `semantic_boundary`
- `asset_class`: `atomic`, `grouped-support`, `background-support`, `preview-reference`, or `candidate`
- `reuse_status`: `production-ready`, `draft-candidate`, `support-only`, or `blocked`
- `planned_route`: `extract`, `reconstruct`, `generate`, `rebuild_downstream`, or `support_only`
- `decision`: `extract_asset`, `rebuild_downstream`, `support_only`, or `requires_user_confirmation`
- `notes`

Use `requires_user_confirmation` only when ambiguity is real and the branch would materially change reuse boundaries, editability, approximation truthfulness, or final claims.

`planned_route` is the planning-time taxonomy stored in `plan_manifest.json`. `decision` remains the current execution-state reflection used in `metadata.json` during rollout.

For UI or dense compositions, the package-level `granularity` block should also record:

- `scope_strategy`: `high-signal-subset` or `full-image-batch`
- `text_handling`: `extract-as-image` or `rebuild-downstream`
- `carrier_glyph_policy`: `split`, `grouped`, or `conditional`
- `background_expectation`: `exact-recovery` or `approximate-accepted`
- `layer_independence`: `static-reuse` or `animation-ready`

## Carrier/Glyph Rule

For icon-in-tile, badge-in-card, glyph-on-plate, or symbol-on-button patterns, prefer separate carrier and glyph layers when either layer may be reused independently or when edge cleanup is easier separately.

This is not a separate stop class or a separate formal gate. Carrier/glyph handling is a branch inside `granularity_alignment` and should be recorded through that decision surface.

Required evidence for carrier/glyph splits:

- carrier and glyph have separate object records
- carrier and glyph each have their own source-space mask overlay
- glyph layer is checked for carrier/background color residue
- carrier layer is checked for dirty edges near glyph holes or symbol boundaries
- grouped convenience layer, if present, is marked `grouped-support` or `support-only`

If the glyph still contains carrier or background color after splitting, set `quality_checks.background_residue=blocked` or keep `reuse_status=draft-candidate`.

When a stylized carrier is heavily occluded by the glyph, classify the cleanup path before repair:

- `hidden-pixel recoverable`
- `design-like redraw candidate`
- `approximate support-only`

Do not accept generic inpaint output as the final carrier by default in these cases.

## UI-Specific Repair Routing

Use the object type to choose the repair path:

- `ui-carrier`
  - reconstruction candidate generation
  - border pasteback if the carrier has visible framing or shading
  - candidate scoring before compare/promotion
- `ui-glyph`
  - hard-edge cleanup
  - preserve silhouette
  - only tighten alpha deliberately
  - padded delivery variant when edge breathing room helps downstream reuse
- `carrier-glyph-pair`
  - split first
  - reconstruct carrier separately
  - then clean glyph against the improved carrier/background estimate

When a glyph or carrier is small, prefer upscale-repair-downscale as a formal path rather than hand-wavy “try enlarging it”.

## Draft-Only UI Runs

When mature upstream extraction is missing, do not let a large UI package look finished because it has many files.

Use:

- `candidate` + `draft-candidate` for unreviewed cutouts
- `grouped-support` + `support-only` for plates, row groups, and grouped UI chrome
- `background-support` + `support-only` for approximate clean plates
- `blocked` for layers with dirty glyph edges, missing masks, or unaccepted reconstruction

Final reporting should separate:

- `production-ready assets`
- `draft candidate assets`
- `support-only layers`
- `blocked assets`

Do not count large plates, `background_clean`, grouped rows, or screenshot-level support layers as atomic production assets.

For ordinary text, labels, numeric values, and form-like UI content, keep a placeholder/object record and route to `rebuild_downstream` unless the text is visually fidelity-critical.
