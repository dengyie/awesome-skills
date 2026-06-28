# Pipeline Recipes

## Purpose

Use these recipes to choose an extraction path before creating production assets. The bundled scripts do not run these tools; they record and validate the evidence that the chosen pipeline produced.

Treat professional upstream extraction as the normal production path. This skill is the packaging, QA, and delivery tail of the pipeline, not a replacement for detection, segmentation, matting, or reconstruction.

Think in three layers:

- capability preparation: check local tools or external evidence before extraction
- segmentation execution adapter: run or receive professional upstream outputs and normalize them with the import contract
- quality adjudication: previews, warning-only visual audit, manual/user acceptance, structural validation, and manifest export

Also think in object types before choosing tools:

- `ui-carrier`
- `ui-glyph`
- `carrier-glyph-pair`
- `soft-edge-logo-brand-mark`
- `outlined-illustration-logo`
- `flat-support-plate`
- `photo-object-matte`

Before choosing a recipe, run `scripts/check_extraction_environment.py` or otherwise confirm the upstream capability. The preflight report must distinguish installed tooling from runtime-ready and production-ready capability across `segmentation`, `matting`, `reconstruction`, and `environment`, and it should explicitly report `recommended_installs`, `missing_roles`, and `why_it_matters`. If local SAM2/Grounded-SAM/rembg/BiRefNet/RMBG-style tooling is unavailable and the user has not provided external assets, run the Preflight Tooling Recommendation Gate: recommend `install-or-activate-tools`, ask for `external-professional-outputs`, or record that the user chose `draft-packaging-only`.

Do not use Pillow, OpenCV, or skimage as the primary production segmenter. They are suitable for alpha compositing, PNG persistence, source-space mask expansion, preview generation, simple repair helpers, and metadata packaging. If the mature segmenter path is unavailable, ask the user for installation, external outputs, or draft-only packaging instead of silently falling back to coordinate crops.

Recipes do not create new stop classes. Stop behavior still comes from the canonical gate taxonomy in `workflow.md`.

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

See `grounded-sam-pipeline.md` for the standard adapter input/output contract. Upstream input should be source image plus boxes, points, masks, or grounded prompts. Upstream output should be source-space masks, tight RGBA assets, and a provenance manifest.

Recommended upstream roles:

- detection / grounding: GroundingDINO, Grounded-SAM, or equivalent prompt-to-region tooling
- segmentation: SAM2, SAM, Grounded-SAM, or equivalent source-space mask generator
- alpha refinement / matting: rembg, BiRefNet, RMBG, or equivalent matte refinement tool
- background reconstruction: IOPaint, LaMa, inpainting tools, or manual paint repair
- packaging / QA: this skill's scripts

Missing capability impact:

- Missing SAM2 or grounded detector: object boundaries may need manual prompts or may be less reliable.
- Missing rembg/BiRefNet/RMBG: transparent PNG alpha edges may keep halos, dark fringes, or background residue.
- Missing dedicated reconstruction tooling: `background_clean.png` or carrier repair can only proceed through manual redraw or approximate reconstruction and should stay `needs-review`.

Record this recipe as `grounded-segmentation-matting-repair`.

For small, stylized, hard-edge UI assets, generic matting tools may degrade shape fidelity or remove intentional details. Prefer visually verified segmentation plus targeted edge cleanup over mechanically forcing a matting tool on every asset.

For complex flat UI, run this recipe first on a high-signal subset rather than attempting a full 100-layer atomization pass. Good first-pass targets include logos, nav icons, status dots, pins, checkboxes, chart marks, row glyphs, badges, and small foreground controls.

For icon-in-tile or glyph-on-plate structures, segment or reconstruct the carrier tile and foreground glyph separately when semantic reuse matters.

For `carrier-glyph-pair`, treat the task as a reconstruction workflow, not a one-pass cutout:

```text
grounded detection / SAM2 masks
-> carrier mask + glyph mask
-> glyph exclusion dilation
-> generate_ui_carrier_candidates.py
-> score_candidate_assets.py
-> compare_candidate_assets.py
-> promote_candidate_asset.py
-> generate_ui_glyph_cleanup_candidates.py
-> score_candidate_assets.py
-> compare_candidate_assets.py
-> promote_candidate_asset.py
```

Imported objects from this recipe should start as `asset_class: candidate` and `reuse_status: draft-candidate`. Promote only after mask overlay, alpha inspection, warning audit, and manual/user acceptance pass.

For stylized UI carriers with bevels, inset borders, lighting, or texture, treat glyph removal as a reconstruction or redraw problem, not a generic inpaint task. Do not promote a carrier layer cleaned only by generic inpaint when the original design language is materially altered or flattened.

Preferred UI carrier strategies:

- `inpaint-direct`
- `center-only-rebuild`
- `center-rebuild-with-border-pasteback`
- `manual-texture-reconstruct`

Fallback ladder:

- `IOPaint direct fail -> center-only rebuild`
- `rebuild still flat -> manual texture reconstruct candidate`
- do not promote a worse candidate only because it used a more “professional” tool

For hard-edge UI glyphs, do not default to generic matting. Prefer:

```text
segmentation mask
-> carrier/background estimate
-> generate_ui_glyph_cleanup_candidates.py
-> score_candidate_assets.py
-> compare_candidate_assets.py
```

Preferred glyph cleanup strategies:

- `keep-current-alpha-recolor`
- `tile-subtract`
- `tile-subtract-tight`
- `padded-delivery-variant`

Fallback ladder:

- `glyph cleanup over-cuts -> revert to keep-current-alpha-recolor`
- preserve silhouette before chasing perfectly clean alpha

For small assets under roughly 128 px, prefer:

```text
upscale_repair_downscale.py
-> repair at 2x or 4x
-> compare candidate outputs after downscale
```

Small-asset cleanup done only at native tiny resolution should be treated as a weaker path when quality matters.

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
- per-layer `asset_class` and `reuse_status`
- package-level `asset_summary` counts

If this evidence is missing, the package is only a preview or draft and must remain `needs-review` or `blocked`.

Background clean plates and support plates produced by inpainting, manual paint, or reconstruction are valid supporting assets, but record them as approximate reconstructed layers with reconstruction provenance. They are not exact automatic segmentation results.

## Capability Outcomes

- `production-capable`: mature upstream segmentation and refinement are available, and the package can proceed through the normal import/QA/validation path
- `draft-packaging-only`: mature upstream extraction is unavailable, so the skill may initialize, stage, archive, or package evidence, but it must not claim production extraction

For reconstruction specifically, do not treat `torch` or `onnxruntime` as a sufficient condition for `production-capable`. They are environment support, not a dedicated reconstruction path.

`qa.status=pass` requires `metadata.capability.production_capable=true`. Draft-only or unrecorded tooling preflight cannot support `pass`.
