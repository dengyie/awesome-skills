# Split Image Assets Pipeline Refactor Design

## Goal

Refactor `split-image-assets` from a generic asset-package helper into a quality-gated layer extraction workflow inspired by mature pipelines:

- Grounded-SAM/SAM2 style detection, segmentation, and mask provenance.
- Matting/refinement tools such as rembg, BiRefNet, or RMBG for production alpha.
- Inpainting tools such as IOPaint/LaMa/Stable Diffusion for honest background repair.
- Qwen-Image-Layered style RGBA layer decomposition and recursive layer inventory.

## Design

The skill must stay deterministic at its core. Bundled scripts do not run segmentation, matting, inpainting, or image generation. Instead, the skill records which external/manual pipeline produced each layer and rejects packages that lack quality evidence.

The package contract gains an `extraction_pipeline` block in `metadata.json`. It records the selected recipe, stages, quality gates, and upstream tool provenance. Each reusable object layer gains `layer_kind`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`.

## Current Data Flow

```text
source image
-> init_asset_package.py
-> check_extraction_environment.py
-> granularity alignment gate
-> semantic analysis in metadata.analysis
-> external mature extraction pipeline
-> _staging/ for active upstream outputs
-> import_external_assets.py
-> build_previews.py
-> build_quality_previews.py
-> record_quality_review.py
-> validate_asset_package.py
-> _archive_intermediate/ for retained intermediates
-> export_asset_manifest.py
-> qa_report.md and final user-facing summary
```

### 1. Package Initialization

`scripts/init_asset_package.py` copies the source image into `source/source_original.png`, creates the default `assets/`, `masks/`, `previews/`, `_staging/`, and `_archive_intermediate/` directories, writes `metadata.json`, and initializes `qa_report.md` with `Final status: needs-review`.

Initialized packages are intentionally not valid final packages. They still need semantic analysis, extraction pipeline metadata, object inventory, quality evidence, and inspection artifacts.

### 2. Extraction Capability And Granularity Gates

`scripts/check_extraction_environment.py` checks optional local extraction modules without installing anything:

- Pillow
- OpenCV
- Torch
- rembg
- SAM2
- segment-anything

The report recommends whether to use a local mature pipeline, ask for external cutouts/masks, or continue draft-only. If a mature segmentation/matting path is unavailable and no external assets were supplied, the skill must not claim production extraction.

The capability gate now reports `production_capable` plus `missing_for_production` so agents can distinguish "some tools exist" from "production-grade segmentation and refinement is locally available."

Before cutting pixels, the agent must also align split granularity with the user: module-level, component-level, atomic-layer, or production-editable reconstruction; image text versus live downstream text; approximate versus exact background repair; and animation-ready versus static layers.

Pillow, OpenCV, and skimage are helper tools for compositing, source-space mask expansion, preview generation, repair helpers, and packaging. They are not the primary segmenter for production assets.

### 3. Semantic Analysis

The user or agent records:

- `metadata.analysis.visual_hierarchy`
- `metadata.analysis.recommended_split_plan`

This is the anti-rectangle gate. A layer must represent a semantic object, background, frame, label, route, shadow, decoration, or control. A rectangle is only a storage bbox around a semantic mask.

For complex UI, the workflow should start with a high-signal subset such as logos, nav icons, status dots, pins, checkboxes, chart marks, badges, or row glyphs before expanding to more atoms. For icon-in-tile or glyph-on-plate patterns, the carrier tile and foreground glyph should be separate layers when independent reuse or mask cleanup matters.

### 4. External Mature Pipeline

The skill treats mature image tools as upstream producers, not bundled dependencies. Supported upstream families include:

- Grounded-SAM, Grounded-SAM-2, SAM, or SAM2 for segmentation masks.
- rembg, BiRefNet, RMBG, or equivalent matting tools for alpha refinement.
- IOPaint, LaMa, Stable Diffusion inpainting, or manual paint work for background repair.
- Qwen-Image-Layered, LayerDiffuse, LayerD, See-through style tools, or manual PSD-like editing for layer proposals.

The repository does not vendor model code, weights, or runtime environments. The stable boundary is the adapter layer and metadata contract.

### 5. External Output Import

`scripts/import_external_assets.py` normalizes mature-tool outputs into the package:

- copies transparent PNGs into `assets/`
- copies masks into `masks/`
- writes or updates object records in `metadata.objects`
- records `metadata.extraction_pipeline.recipe`
- records `metadata.extraction_pipeline.stages`
- appends structured `metadata.extraction_pipeline.tools`
- sets imported object `quality_checks` to `needs-review`

The importer validates input files and metadata before copying, rejects unsafe `object-id` path segments, and keeps copied paths inside the package.

The importer requires masks to be source-space masks matching the source dimensions. Tight bbox masks must be expanded to source coordinates before import or retained as intermediates in `_staging/`.

### 6. Preview And QA Evidence

`scripts/build_previews.py` creates ordinary inspection previews:

- white-background preview
- checkerboard preview
- overview decomposition
- 2x2 sprite sheet

`scripts/build_quality_previews.py` creates segmentation QA evidence:

- source/mask overlay
- alpha inspection preview

Preview files are evidence for inspection. They are never production substitutes for reusable assets.

### 7. Manual Quality Review Recording

`scripts/record_quality_review.py` records the human or agent inspection result after previews are generated:

- semantic hierarchy and recommended split plan
- granularity mode, confirmation, and notes
- inspected pipeline quality gates
- object-level mask, alpha, background residue, and reuse checks
- package QA status
- review notes appended to `qa_report.md`

This script exists to avoid a common manual-test failure: imported layers stay `needs-review`, semantic analysis is missing, or `qa.status` is promoted by hand without matching object-level evidence. It rejects `qa.status=pass` unless every required object quality check is `pass`.

Crop-only or estimated layers are draft evidence by default. `record_quality_review.py --confirm-crop-layer` records per-layer human confirmation when a bbox/manual-estimated crop is explicitly accepted for production reuse.

### 8. Structural Validation

`scripts/validate_asset_package.py` validates the package contract:

- required directories and files exist
- metadata is parseable
- package-relative paths do not escape the package
- source dimensions match metadata
- semantic analysis exists
- extraction pipeline recipe, stages, tools, and quality gates exist
- object inventory is non-empty
- production PNG layers include alpha
- source-space masks match source dimensions
- agreed granularity metadata is recorded
- unarchived external model folders or temporary manifests are not loose in the package root
- ordinary inspection previews and segmentation-quality previews exist for every reusable object layer
- object records include composition order, semantic boundary, mask source, alpha source, and quality checks
- package `qa.status` cannot be `pass` unless every required object quality check is `pass`
- crop-only or estimated layers cannot support `qa.status=pass` without `manual_review_confirmed=true`
- approximate or reconstructed layers must record `reconstruction_provenance` and cannot support `qa.status=pass` without manual confirmation
- helper-only sources such as Pillow/OpenCV/skimage thresholds or crop alpha cannot support `qa.status=pass` without manual confirmation
- preview references, including nested quality preview paths, resolve inside the package

Validation proves structural evidence is present. It does not prove visual perfection.

### 9. Downstream Manifest Export

`scripts/export_asset_manifest.py` creates `asset_manifest.json` for downstream consumers:

- renderer integration
- animation pipeline handoff
- design-tool import
- manual review queues

The manifest is sorted by `composition_order`, uses package-relative paths, and includes per-layer quality status. It is generated from `metadata.json`; it is not the source of truth.

## Quality Gates

A package can validate structurally only when it records:

- semantic visual hierarchy and split plan
- extraction pipeline recipe and ordered stages
- mask provenance and alpha provenance per production layer
- object-level semantic boundary
- object-level quality checks for mask, alpha, edges, and reuse
- manual-review flags for low-confidence, AI-assisted, estimated, or unrepaired regions

The validator remains structural and metadata-focused. It does not judge visual beauty, but it blocks packages that lack the evidence needed to judge segmentation quality.

## Files

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/references/qa-standards.md`
- `split-image-assets/references/manual-review.md`
- `split-image-assets/references/pipeline-recipes.md`
- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/check_extraction_environment.py`
- `split-image-assets/scripts/import_external_assets.py`
- `split-image-assets/scripts/build_previews.py`
- `split-image-assets/scripts/build_quality_previews.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/scripts/export_asset_manifest.py`
- `split-image-assets/tests/test_skill_package.py`
- `docs/usage/split-image-assets.md`

## Test Readiness

Use this test loop before manual image trials:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover split-image-assets\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover tests -v
$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets
git diff --check
```

For a manual package trial, the expected command sequence is:

```powershell
python split-image-assets\scripts\init_asset_package.py source.png output-package
python split-image-assets\scripts\check_extraction_environment.py
python split-image-assets\scripts\import_external_assets.py output-package --object-id main_object --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject from upstream mask" --asset main.png --mask mask_main.png --mask-source sam2 --alpha-source rembg --tool-name SAM2 --tool-role segmentation --tool-version external
python split-image-assets\scripts\build_previews.py output-package
python split-image-assets\scripts\build_quality_previews.py output-package
python split-image-assets\scripts\record_quality_review.py output-package --visual-hierarchy background --visual-hierarchy "main object" --recommended-split-plan "Keep the main object separate from the background." --granularity-mode atomic-layer --granularity-confirmed --granularity-note "Atomic foreground layers; text rebuilt downstream." --quality-gate "mask overlay inspected" --object-id main_object --mask-alignment pass --alpha-edges pass --background-residue pass --reuse-readiness pass --qa-status pass --review-note "Manual inspection accepted the imported layer."
python split-image-assets\scripts\archive_intermediates.py output-package --run-id sam-pass-001
python split-image-assets\scripts\validate_asset_package.py output-package
python split-image-assets\scripts\export_asset_manifest.py output-package
```

Expected failure modes during testing:

- An initialized package fails validation until analysis, pipeline metadata, object inventory, quality evidence, and previews are added.
- Imported layers default to `needs-review`; a user or reviewer must upgrade quality checks after inspection.
- `record_quality_review.py` is the supported path for upgrading quality checks and QA status after inspection.
- `qa.status=pass` is blocked unless all required object quality checks are `pass`.
- bbox/manual-estimated crop layers remain draft-only unless per-layer manual confirmation is recorded.
- Absolute paths or `..` path escapes in metadata are rejected.
- The scripts do not run SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, inpainting, or generation directly.

## Non-Goals

- Do not vendor SAM, rembg, Qwen-Image-Layered, or any model weights.
- Do not claim automatic extraction quality from deterministic scripts.
- Do not make visual QA fully automatic.
