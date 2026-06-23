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

## Manual Review Output

When manual review is needed, report:

- package path
- affected object IDs
- issue type
- preview files to inspect
- recommended correction area
- failed quality gate: mask alignment, alpha edges, background residue, or reuse readiness
- whether the package is `needs-review` or `blocked`

## Honesty Rule

Do not upgrade a package to `pass` because it looks acceptable in a small preview. Use `needs-review` when uncertainty remains in production assets, masks, or repaired background.

Do not upgrade a package to `pass` when the asset set lacks the image's core semantic layers. Structural validity is not the same thing as reusable decomposition.
