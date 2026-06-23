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
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/tests/test_skill_package.py`
- `docs/usage/split-image-assets.md`

## Non-Goals

- Do not vendor SAM, rembg, Qwen-Image-Layered, or any model weights.
- Do not claim automatic extraction quality from deterministic scripts.
- Do not make visual QA fully automatic.
