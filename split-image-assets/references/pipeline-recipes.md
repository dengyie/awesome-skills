# Pipeline Recipes

## Purpose

Use these recipes to choose an extraction path before creating production assets. The bundled scripts do not run these tools; they record and validate the evidence that the chosen pipeline produced.

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

Typical tool families:

- Grounded-SAM, Grounded-SAM-2, SAM, or SAM2 for text-guided masks and object boundaries
- rembg, BiRefNet, RMBG, or equivalent matting tools for transparent PNG refinement
- IOPaint, LaMa, Stable Diffusion inpainting, or manual paint work for `background_clean.png`
- human inspection for edge contamination, hidden-pixel recovery, and reuse readiness

Record this recipe as `grounded-segmentation-matting-repair`.

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
