# UI Atomic Split Planning

Use this reference before extracting complex UI screenshots, dashboards, app mockups, badges, icon tiles, or dense interface panels.

The problem is not only "can the pixels be cut out"; it is "what should become reusable". Build a semantic split plan before running a segmenter or importing upstream assets.

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
- `decision`: `must_extract`, `rebuild_downstream`, `support_only`, `skip_for_now`, or `requires_user_confirmation`
- `notes`

Use `requires_user_confirmation` when a decision affects editability, localization, animation readiness, approximate reconstruction acceptance, or final production claims.

For UI or dense compositions, the package-level `granularity` block should also record:

- `scope_strategy`: `high-signal-subset` or `full-image-batch`
- `text_handling`: `extract-as-image` or `rebuild-downstream`
- `carrier_glyph_policy`: `split`, `grouped`, or `conditional`
- `background_expectation`: `exact-recovery` or `approximate-accepted`
- `layer_independence`: `static-reuse` or `animation-ready`

## Carrier/Glyph Rule

For icon-in-tile, badge-in-card, glyph-on-plate, or symbol-on-button patterns, prefer separate carrier and glyph layers when either layer may be reused independently or when edge cleanup is easier separately.

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
