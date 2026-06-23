# Split Image Assets

Use `split-image-assets` when a source image needs to become a reusable asset package instead of a single preview image.

The skill helps produce transparent PNG object layers, mask files, `background_clean.png`, `metadata.json`, `qa_report.md`, and inspection previews such as `sprite_sheet_2x2.png`.

The deterministic script layer does not perform segmentation. Use AI image editing, segmentation tools, manual editing, or user-provided cutouts to create object assets, then use the scripts to initialize, preview, and validate the package.

For quality-first extraction, use a Grounded-SAM/SAM2 style pipeline: semantic analysis, text-guided detection, segmentation, alpha refinement with rembg/BiRefNet/RMBG-style tools, background repair with inpainting or manual paint work, then QA. For layer-first decomposition, use Qwen-Image-Layered style RGBA layer proposals, then inspect every layer before treating it as production-ready.

Start by recording a semantic layer hierarchy in `metadata.analysis.visual_hierarchy`. Split by meaning: background/backplate, frame or UI chrome, main subjects, connection paths, labels, buttons, decorations, shadows, and overlays. A rectangular crop is only acceptable as a tight storage bbox around a semantic mask; rectangular crop packages are not complete asset packages.

## Output Package

```text
asset-package/
  source/source_original.png
  assets/main_object_transparent.png
  assets/background_clean.png
  masks/mask_main.png
  previews/sprite_sheet_2x2.png
  asset_manifest.json
  metadata.json
  qa_report.md
```

`metadata.json` must also include `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `extraction_pipeline`, and per-object quality evidence so reviewers can tell whether extraction followed the image structure instead of only cutting page regions.

## Basic Commands

```bash
python split-image-assets/scripts/init_asset_package.py source.png output-package
python split-image-assets/scripts/import_external_assets.py output-package --object-id main_object --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject from SAM2 mask" --asset main.png --mask mask_main.png --mask-source sam2 --alpha-source rembg --tool-name SAM2 --tool-role segmentation --tool-version external
python split-image-assets/scripts/build_previews.py output-package
python split-image-assets/scripts/build_quality_previews.py output-package
python split-image-assets/scripts/record_quality_review.py output-package --visual-hierarchy background --visual-hierarchy "main object" --recommended-split-plan "Keep the main object separate from the background." --quality-gate "mask overlay inspected" --object-id main_object --mask-alignment pass --alpha-edges pass --background-residue pass --reuse-readiness pass --qa-status pass --review-note "Manual inspection accepted the imported layer."
python split-image-assets/scripts/validate_asset_package.py output-package
python split-image-assets/scripts/export_asset_manifest.py output-package
```

`asset_manifest.json` is the downstream handoff file for renderers, animation tooling, design imports, or manual review queues. It is generated from `metadata.json`, sorted by `composition_order`, and uses package-relative paths.

## QA

Use `pass` only when reusable assets, masks, metadata, previews, and background repair are acceptable. Use `needs-review` when edge quality, AI-assisted regions, object roles, or background repair need manual review. Use `blocked` when required files are missing or the package cannot be reused safely.

Use `needs-review` or `blocked` when the background is only a reconstructed approximation, when core layers are missing, or when the result is mostly rectangular crops.

Per-object `quality_checks` should cover mask alignment, alpha edges, background residue, and reuse readiness. Missing mask or alpha provenance is a review blocker even when the PNG file opens correctly. Record `composition_order` so downstream renderers can rebuild the layer stack, and do not set package `qa.status` to `pass` unless every required object quality check is `pass`.

Use `record_quality_review.py` after inspecting previews to update `metadata.json` and append `qa_report.md` together. This prevents the common failure where imported layers remain `needs-review`, semantic analysis is missing, or `qa.status` is promoted without matching object-level evidence.

Validation now requires both ordinary inspection previews from `build_previews.py` and quality previews from `build_quality_previews.py` for each reusable object layer. A package without preview evidence is incomplete even if the transparent PNGs and masks exist.
