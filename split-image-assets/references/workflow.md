# Split Image Assets Workflow

## Purpose

Use this workflow to turn a single source image into a reusable asset package. Optimize for reusable files, clear provenance, inspectable previews, and honest QA status.

## Stages

1. Intake the source image and identify the desired output package directory.
2. Run `scripts/init_asset_package.py` if the package does not already exist.
3. Read `pipeline-recipes.md` and choose a pipeline recipe.
4. Analyze before extraction:
   - source dimensions
   - semantic layer hierarchy from background to foreground
   - main object
   - secondary objects
   - background type
   - object overlap
   - shadows
   - complex edge regions
   - likely manual-review risks
5. Pause for user decision sync when layer boundaries, grouping, text ownership, background repair, animation readiness, or low-confidence masks require product judgment.
6. Write `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `extraction_pipeline`, and the object inventory into `metadata.json`.
7. Produce or collect reusable assets through AI image tools, segmentation tools, manual editing, or user-provided files.
8. Normalize external outputs with `scripts/import_external_assets.py` when assets come from SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual editing, or user-provided files.
9. Record composition order, mask source, alpha source, semantic boundary, and object-level quality checks for every reusable layer. Use `scripts/record_quality_review.py` after inspection so semantic analysis, quality gates, QA status, and `qa_report.md` stay synchronized.
10. Keep individual objects separate before creating grouped or preview outputs.
11. Generate previews with `scripts/build_previews.py`.
12. Generate segmentation-quality previews with `scripts/build_quality_previews.py`.
13. Inspect previews and, when appropriate, update object quality checks and QA status with `scripts/record_quality_review.py`.
14. Validate the package with `scripts/validate_asset_package.py`.
15. Export a downstream layer manifest with `scripts/export_asset_manifest.py`.
16. Report the package path, final status, manifest path, and any manual correction points.

## Status Meanings

- `pass`: structure is valid and inspection found no blocking reuse issue.
- `needs-review`: package is usable as a draft, but one or more assets need human inspection or correction.
- `blocked`: package cannot be treated as reusable until missing files or serious quality issues are resolved.

## Do Not

- Do not treat a 2x2 preview as the final asset.
- Do not treat rectangular crops, grid slices, or page regions as assets unless each crop is only a tight bbox around a semantic mask.
- Do not merge separate objects into one layer unless the grouped layer is explicitly additional.
- Do not hide AI-assisted fills or uncertain edges.
- Do not claim the scripts extracted objects from the source image.
- Do not claim segmentation quality when `extraction_pipeline` or per-object quality evidence is missing.

## Layer Decomposition Checklist

Before cutting pixels, name the reusable layers that a downstream renderer would stack:

- background or reconstructed backplate
- global frame, chrome, navigation, or other structural UI
- main subjects or domain regions
- connection/path/network layers
- labels, badges, node buttons, or controls
- decorative objects and texture details
- shadows, glows, or overlay effects

If the plan only names rectangles such as "top left", "map area", or "2x2 tile", stop and redo the analysis.

## User Decision Sync

When a split choice affects future reuse, editing, localization, animation, or visual truth, ask the user one focused question before continuing. Include your recommended answer. Do not batch multiple questions unless the user asks for a full grill-me style interrogation.

## Quality-Gated Pipeline Checklist

Before claiming reuse quality, record:

- selected recipe such as `grounded-segmentation-matting-repair` or `layered-rgba-decomposition`
- ordered stages from semantic analysis through QA review
- upstream tools and manual operations used for masks, alpha, background repair, and layer proposals
- quality gates inspected for mask alignment, alpha edges, background residue, and reuse readiness
- object-level `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`

## Downstream Manifest

Run `scripts/export_asset_manifest.py` after validation when another tool needs a stable layer list. The script writes `asset_manifest.json` by default, sorted by `composition_order`, with package-relative asset and mask paths plus quality status per layer.

The manifest is a consumer-facing index. It does not replace `metadata.json`, `qa_report.md`, or manual inspection.
