# Pipeline Recipes

## Purpose

Use these recipes to choose an extraction path before creating production assets. The bundled scripts do not run these tools; they record and validate the evidence that the chosen pipeline produced.

Treat professional upstream extraction as the normal production path. This skill is the packaging, QA, and delivery tail of the pipeline, not a replacement for detection, segmentation, matting, or reconstruction.

Before choosing a recipe, run `scripts/check_extraction_environment.py` or otherwise confirm the upstream capability. If local SAM2/Grounded-SAM/rembg/BiRefNet/RMBG-style tooling is unavailable and the user has not provided external assets, keep the package draft-only or pause for the user to choose installation, external outputs, or manual editing.

Do not use Pillow, OpenCV, or skimage as the primary production segmenter. They are suitable for alpha compositing, PNG persistence, source-space mask expansion, preview generation, simple repair helpers, and metadata packaging. If the mature segmenter path is unavailable, ask the user for installation, external outputs, or draft-only packaging instead of silently falling back to coordinate crops.

## Recommended Default: Grounded Segmentation, Matting, And Repair

Use this when segmentation quality matters more than speed.

```text
semantic-analysis
-> detection
-> segmentation
-> alpha-refinement
-> background-repair
-> layer-packaging
-> qa-review
```

Typical tool roles:

- detection: GroundingDINO, grounded prompts, or equivalent prompt-to-region tooling
- segmentation: Grounded-SAM, Grounded-SAM-2, SAM, or SAM2 for object boundaries and source-space masks
- alpha refinement / matting: rembg, BiRefNet, RMBG, or equivalent alpha cleanup tools
- reconstruction / inpaint: IOPaint, LaMa, Stable Diffusion inpainting, or manual paint work for `background_clean.png`
- packaging / QA: `import_external_assets.py`, `build_previews.py`, `build_quality_previews.py`, `record_quality_review.py`, `validate_asset_package.py`, and `export_asset_manifest.py`

Record this recipe as `grounded-segmentation-matting-repair`.

For complex flat UI, run this recipe first on a high-signal subset rather than attempting a full 100-layer atomization pass. Good first-pass targets include logos, nav icons, status dots, pins, checkboxes, chart marks, row glyphs, badges, and small foreground controls.

For icon-in-tile or glyph-on-plate structures, segment or reconstruct the carrier tile and foreground glyph separately when semantic reuse matters.

## Layer-First Candidate: Qwen-Image-Layered Style Decomposition

Use this when the source image is already a designed composition and the desired result is editable RGBA layers.

```text
semantic-analysis
-> layered-decomposition
-> recursive-layer-review
-> alpha-refinement
-> layer-packaging
-> qa-review
```

This route can propose multiple RGBA layers quickly, but every layer still needs mask, alpha, boundary, and reuse QA before it can be treated as production-ready.

Record this recipe as `layered-rgba-decomposition`.

## Specialized Routes

- Use See-through style workflows for anime character art, Live2D preparation, depth ordering, and PSD-like outputs.
- Use LayerD style workflows for flat UI, posters, diagrams, or graphic designs that should become SVG/PSD-like editable elements.
- Use LayerDiffuse style workflows when the source of truth is generated transparent imagery rather than extraction from a fixed flattened image.

## Required Evidence

Every recipe must record:

- selected `recipe`
- ordered `stages`
- upstream `tools` with `name`, `role`, and `version`
- `quality_gates` inspected before final status
- per-layer `composition_order`, `mask_source`, `alpha_source`, `semantic_boundary`, and `quality_checks`

If this evidence is missing, the package is only a preview or draft and must remain `needs-review` or `blocked`.

Background clean plates and support plates produced by inpainting, manual paint, or reconstruction are valid supporting assets, but record them as approximate reconstructed layers with reconstruction provenance. They are not exact automatic segmentation results.

## Capability Outcomes

- `production-capable`: mature upstream segmentation and refinement are available, and the package can proceed through the normal import/QA/validation path
- `draft-packaging-only`: mature upstream extraction is unavailable, so the skill may initialize, stage, archive, or package evidence, but it must not claim production extraction
