# Manual Review

## Enter Manual Review When

- segmentation confidence is low
- foreground and background colors are similar
- objects overlap heavily
- transparent or reflective materials dominate the image
- fuzzy, smoky, glowing, or soft edges are important
- background repair looks unnatural
- object count or role assignment is uncertain
- mask previews reveal edge contamination

## Manual Review Output

When manual review is needed, report:

- package path
- affected object IDs
- issue type
- preview files to inspect
- recommended correction area
- whether the package is `needs-review` or `blocked`

## Honesty Rule

Do not upgrade a package to `pass` because it looks acceptable in a small preview. Use `needs-review` when uncertainty remains in production assets, masks, or repaired background.

