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

## Manual Review Output

When manual review is needed, report:

- package path
- affected object IDs
- issue type
- preview files to inspect
- recommended correction area
- failed quality gate: mask alignment, alpha edges, background residue, or reuse readiness
- whether the package is `needs-review` or `blocked`

## Practical Checks

- For icon-in-tile, badge-in-card, or glyph-on-plate structures, inspect whether the carrier layer and foreground glyph should be separated. If the mask mixes them and cleanup becomes awkward, split carrier + glyph before claiming reuse readiness.
- A mostly black source-space mask is normal when the object is small. Do not judge the layer from `masks/*.png` alone; inspect `assets/*.png` for tight transparent reuse and inspect `*_mask_overlay.png` to verify source alignment.

## Honesty Rule

Do not upgrade a package to `pass` because it looks acceptable in a small preview. Use `needs-review` when uncertainty remains in production assets, masks, or repaired background.

Do not upgrade a package to `pass` when the asset set lacks the image's core semantic layers. Structural validity is not the same thing as reusable decomposition.
