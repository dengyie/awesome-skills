# Manual Review

## Enter Manual Review When

- segmentation confidence is low
- foreground and background colors are similar
- objects overlap heavily
- transparent or reflective materials dominate the image
- fuzzy, smoky, glowing, or soft edges are important
- background repair looks unnatural
- object count or role assignment is uncertain
- the package looks like rectangular crops instead of semantic layers
- extraction pipeline, upstream tool provenance, or quality gates are missing
- mask source or alpha source is unclear for a reusable production layer
- the background is reconstructed from a flattened image and hidden pixels cannot be verified
- mask previews reveal edge contamination
- icon-in-tile, badge-in-card, or glyph-on-plate edges look merged or contaminated
- a source-space mask looks mostly black and someone is unsure whether that is a QA mask or a broken asset
- source-space mask overlay reveals contamination even though the preview asset looks clean
- transparent asset preview looks acceptable, but the real RGBA layer still carries dark fringe or base-color residue
- approximate background or support layers are present without reconstruction provenance
- the user asked for atomic split, but the delivered package is still component-level grouped layers
- `granularity.scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, or `layer_independence` are missing on a UI-like package
- `_staging/quality/quality_audit.json` reports `edge-halo`, `color-residue`, `detached-fragments`, `smear-artifact`, `over-flat-reconstruction`, `style-mismatch-reconstruction`, `hard-alpha-risk`, `support-layer-misclassified`, or `carrier-glyph-cross-contamination`
- `asset_class` or `reuse_status` makes draft candidates, support-only layers, or blocked layers look production-ready
- promoted repair candidates have no compare evidence or no selection reason
- promoted repair candidates have a compare image but no compare manifest

## Manual Review Output

When manual review is needed, report:

- package path
- affected object IDs
- issue type
- preview files to inspect
- recommended correction area
- failed quality gate: mask alignment, alpha edges, background residue, or reuse readiness
- whether the package is `needs-review` or `blocked`
- production-ready asset count, draft candidate count, support-only layer count, and blocked count

## Practical Checks

- For icon-in-tile, badge-in-card, or glyph-on-plate structures, inspect whether the carrier layer and foreground glyph should be separated. If the mask mixes them and cleanup becomes awkward, split carrier + glyph before claiming reuse readiness.
- After carrier/glyph separation, inspect whether the glyph still carries carrier/background color. If yes, set `quality_checks.background_residue=blocked` or keep `reuse_status=draft-candidate`.
- Large plates, `background_clean`, grouped UI chrome, and screenshot-level support layers should be `support-only` unless explicitly accepted as production reusable atomic assets.
- A mostly black source-space mask is normal when the object is small. Do not judge the layer from `masks/*.png` alone; inspect `assets/*.png` for tight transparent reuse and inspect `*_mask_overlay.png` to verify source alignment.
- If more than one repair candidate exists, inspect the compare artifact before promotion. If only one candidate exists, record why direct promotion was acceptable.
- Inspect the compare manifest, not just the compare image. A good compare should record criteria, review focus, risks, and candidate asset paths.

## Honesty Rule

Do not upgrade a package to `pass` because it looks acceptable in a small preview. Use `needs-review` when uncertainty remains in production assets, masks, or repaired background.

Do not upgrade a package to `pass` when the asset set lacks the image's core semantic layers. Structural validity is not the same thing as reusable decomposition.

Do not call a draft-only package production reusable because it contains many candidate assets. Report `not production reusable` and keep production-ready counts separate from draft candidate and support-only counts.
