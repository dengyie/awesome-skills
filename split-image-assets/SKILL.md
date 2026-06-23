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
SEMANTIC LAYERS BEFORE RECTANGLES
QUALITY-GATED PIPELINE
DECISION SYNC BEFORE AMBIGUOUS SPLITS
REUSABLE ASSETS BEFORE PREVIEWS
TRANSPARENT PNGS ARE PRODUCTION ASSETS
PREVIEWS ARE INSPECTION ARTIFACTS
NEVER HIDE UNCERTAINTY
```

## Workflow

1. Read `references/workflow.md`.
2. Create or inspect the package directory.
3. Initialize the package with `scripts/init_asset_package.py` when a package does not already exist.
4. Read `references/pipeline-recipes.md` and select an extraction recipe before extraction.
5. Analyze the source image before extraction:
   - visual hierarchy from background to foreground
   - main object
   - secondary objects
   - background type
   - occlusion
   - complex edges
   - transparent, reflective, fuzzy, smoky, or low-contrast regions
   - recommended split plan
6. When the split plan has an ambiguous decision point, follow the Decision Sync Rule before extracting.
7. Read `references/asset-package-contract.md` and update `metadata.json` with the visual hierarchy, recommended split plan, `extraction_pipeline`, and object inventory.
8. Produce or collect reusable assets:
   - transparent PNGs for individual objects
   - source-space masks
   - cleaned background
   - optional shadows and grouped object layers
9. When external tools produced assets, normalize them with `scripts/import_external_assets.py`.
10. Record per-layer segmentation quality evidence: semantic boundary, mask source, alpha source, edge checks, background residue checks, and reuse readiness.
11. Build inspection previews with `scripts/build_previews.py`.
12. Build segmentation-quality previews with `scripts/build_quality_previews.py`.
13. Read `references/qa-standards.md` and inspect the package.
14. Validate structure with `scripts/validate_asset_package.py`.
15. Export a downstream layer manifest with `scripts/export_asset_manifest.py` after validation.
16. Read `references/manual-review.md` before assigning `pass`, `needs-review`, or `blocked`.

## Script Boundaries

The bundled scripts are deterministic packaging helpers. They do not perform segmentation, matting, inpainting, object recognition, or AI image generation.

Use external image tools, AI image editing, manual editing, or user-provided cutouts for the actual extraction work. Good default pipelines are Grounded-SAM/SAM2 style detection and segmentation, matting refinement with rembg/BiRefNet/RMBG-style tools, inpainting or manual paint repair for hidden background, and Qwen-Image-Layered style RGBA layer proposals when the source is a designed composition. Then use this skill to keep the package structure, previews, metadata, and QA evidence consistent.

`scripts/import_external_assets.py` is the standard adapter for mature tool outputs. Use it to copy SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual, or user-provided assets into the package while recording object metadata and upstream tool provenance.

`scripts/build_quality_previews.py` creates QA evidence images such as mask overlays and alpha inspection previews. These previews are inspection artifacts; they do not upgrade a package to `pass` by themselves.

`scripts/export_asset_manifest.py` creates `asset_manifest.json` for downstream renderers, animation pipelines, design tools, or manual review. It records package-relative asset paths sorted by `composition_order`; it does not validate visual quality or replace `metadata.json`.

## Pipeline Quality Rule

Every reusable layer must have provenance. Record which tool or manual process created the mask, which process created or refined alpha, which stage repaired the background, the layer's `composition_order`, and which quality gates were inspected.

The validator checks evidence, not aesthetics. A package can pass structural validation only when it records `metadata.extraction_pipeline`, ordered stages, structured upstream tools, quality gates, and object-level `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`.

Do not set `qa.status` to `pass` when any required object quality check is `needs-review`, `blocked`, or `unknown`.

## Semantic Layer Rule

Do not treat rectangular crops as asset splitting. A package with only page regions, grid cells, or convenient bounding boxes is not complete even when every crop has an alpha channel.

First identify the image's semantic layer hierarchy: background/backplate, frame or chrome, primary subjects, secondary objects, connection layers, labels, buttons or controls, shadows, and decorative details. Extract or reconstruct those layers separately. Use a rectangle only as the storage bbox around a semantic mask, never as the reason an asset exists.

If the hidden background cannot be recovered from one flattened image, create an honest `background_clean.png` approximation or leave the package `needs-review`/`blocked`; do not claim exact recovery.

## Decision Sync Rule

When an image split requires a product or design decision, pause and ask the user one question at a time before extracting or overwriting assets. Provide your recommended answer with each question.

Ask when deciding:

- whether a visually connected region should stay grouped or become separate reusable layers
- whether labels, buttons, text, or UI chrome should be extracted as images or rebuilt downstream
- whether uncertain edges, hidden background, or reconstructed pixels can be accepted as `needs-review`
- whether to prefer exact source preservation, editable layers, animation-ready layers, or quick draft assets
- whether a low-confidence automated mask should be retried with another upstream tool or sent to manual review

If the answer can be determined from the source image, existing metadata, or user-provided requirements, inspect that evidence first. If ambiguity remains, ask exactly one focused question and wait for the answer before continuing that branch.

## Reference Routing

- Read `references/workflow.md` for the full staged workflow.
- Read `references/pipeline-recipes.md` before choosing or documenting the extraction path.
- Read `references/asset-package-contract.md` before creating, renaming, or validating files.
- Read `references/qa-standards.md` before claiming an asset is reusable.
- Read `references/manual-review.md` when confidence is low, edges are complex, objects overlap, or background repair is uncertain.

## Output Expectations

At minimum report:

- package path
- source image
- visual hierarchy and recommended split plan
- extraction pipeline recipe, stages, upstream tools, and quality gates
- object inventory
- generated or collected assets
- previews
- quality preview evidence
- downstream asset manifest
- validation result
- QA status: `pass`, `needs-review`, or `blocked`
- manual-review flags and next correction points
