---
name: split-image-assets
description: Use when turning a source image into a reusable production asset package with independent transparent PNG layers, masks, cleaned background, structured metadata, inspection previews, QA evidence, and manual-review flags. Use for image decomposition, asset splitting, sprite-sheet preview generation, mask/background asset packaging, and workflows where a 2x2 preview must not replace reusable assets.
---

# Split Image Assets

## Mission

Turn a source image into a reusable, inspectable asset package.

This skill is not a one-shot image prompt. Its main output is an asset package with transparent PNGs, masks, cleaned background, metadata, previews, and QA evidence. A 2x2 sprite sheet is only a preview artifact.

## Iron Rules

```text
ANALYZE BEFORE EXTRACTING
REUSABLE ASSETS BEFORE PREVIEWS
TRANSPARENT PNGS ARE PRODUCTION ASSETS
PREVIEWS ARE INSPECTION ARTIFACTS
NEVER HIDE UNCERTAINTY
```

## Workflow

1. Read `references/workflow.md`.
2. Create or inspect the package directory.
3. Initialize the package with `scripts/init_asset_package.py` when a package does not already exist.
4. Analyze the source image before extraction:
   - main object
   - secondary objects
   - background type
   - occlusion
   - complex edges
   - transparent, reflective, fuzzy, smoky, or low-contrast regions
   - recommended split plan
5. Read `references/asset-package-contract.md` and update `metadata.json` with the object inventory.
6. Produce or collect reusable assets:
   - transparent PNGs for individual objects
   - source-space masks
   - cleaned background
   - optional shadows and grouped object layers
7. Build inspection previews with `scripts/build_previews.py`.
8. Read `references/qa-standards.md` and inspect the package.
9. Validate structure with `scripts/validate_asset_package.py`.
10. Read `references/manual-review.md` before assigning `pass`, `needs-review`, or `blocked`.

## Script Boundaries

The bundled scripts are deterministic packaging helpers. They do not perform segmentation, matting, inpainting, object recognition, or AI image generation.

Use external image tools, AI image editing, manual editing, or user-provided cutouts for the actual extraction work. Then use this skill to keep the package structure, previews, metadata, and QA evidence consistent.

## Reference Routing

- Read `references/workflow.md` for the full staged workflow.
- Read `references/asset-package-contract.md` before creating, renaming, or validating files.
- Read `references/qa-standards.md` before claiming an asset is reusable.
- Read `references/manual-review.md` when confidence is low, edges are complex, objects overlap, or background repair is uncertain.

## Output Expectations

At minimum report:

- package path
- source image
- object inventory
- generated or collected assets
- previews
- validation result
- QA status: `pass`, `needs-review`, or `blocked`
- manual-review flags and next correction points

