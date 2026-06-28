# Grounded SAM / SAM2 Upstream Adapter Contract

Use this reference when the split should be production-capable and the user has local tools, cloud tools, or external outputs from Grounded-SAM, Grounded-SAM-2, SAM, SAM2, rembg, BiRefNet, RMBG, or manual refinement.

This skill does not vendor or install model weights. It defines the stable handoff contract so upstream tools can be swapped without weakening package QA.

This is an upstream adapter contract, not a different workflow. Stop and approval behavior still comes from the canonical gate taxonomy.

## Three-Layer Flow

1. Capability preparation:
   - run `scripts/check_extraction_environment.py`
   - confirm whether detection, segmentation, alpha refinement, and background reconstruction are available
   - record `metadata.capability`
2. Segmentation execution adapter:
   - run the external model pipeline or receive its outputs
   - normalize outputs through `scripts/import_external_assets.py`
   - archive retained raw outputs with `scripts/archive_intermediates.py`
3. Quality adjudication:
   - build ordinary previews and quality previews
   - run `scripts/audit_visual_quality.py` for warning-only checks
   - record review outcomes with `scripts/record_quality_review.py`
   - validate and export the manifest

## Standard Input

External upstream tools should receive:

- source image path
- object prompts, text prompts, boxes, points, or masks
- desired granularity mode
- UI split plan when relevant
- output directory under `_staging/<run-id>/`

For UI tasks, prompts should distinguish carrier and glyph when needed, for example:

```text
object_id=status_tile, prompt="rounded blue status tile carrier", box=[x,y,w,h]
object_id=status_glyph, prompt="white check glyph inside status tile", box=[x,y,w,h]
```

## Standard Output

Each upstream object should produce:

- tight RGBA asset PNG
- source-space mask PNG aligned to `source/source_original.png`
- object id
- semantic boundary
- mask source
- alpha source
- confidence
- edge complexity
- upstream provenance

Batch import should use a manifest shaped like `external_manifest_examples/sam2_rembg_manifest.json`.

Required import fields:

- `object_id`
- `role`
- `layer_kind`
- `composition_order`
- `semantic_boundary`
- `asset`
- `mask`
- `mask_source`
- `alpha_source`
- `asset_class`
- `reuse_status`

Default imported layers should remain `asset_class=candidate` and `reuse_status=draft-candidate` until preview evidence and manual/user QA promote them.

## Tool Roles

- detection: GroundingDINO, grounded prompts, manual boxes, or equivalent prompt-to-region tooling
- segmentation: Grounded-SAM, Grounded-SAM-2, SAM, or SAM2 source-space masks
- alpha refinement / matting: rembg, BiRefNet, RMBG, or equivalent alpha cleanup
- reconstruction / inpaint: manual clean plate, IOPaint, LaMa, inpainting tools
- packaging / QA: this skill's scripts

Pillow, OpenCV, and skimage can support image conversion, mask expansion, previews, and deterministic audits. They are helper tools, not primary production segmenters.

## Adapter Commands

Use manifest import when upstream produced multiple objects:

```bash
python split-image-assets/scripts/import_external_assets.py output-package --manifest _staging/run-001/import_manifest.json
python split-image-assets/scripts/archive_intermediates.py output-package --run-id run-001
python split-image-assets/scripts/build_previews.py output-package
python split-image-assets/scripts/build_quality_previews.py output-package
python split-image-assets/scripts/audit_visual_quality.py output-package
```

Use single-object import for quick handoffs:

```bash
python split-image-assets/scripts/import_external_assets.py output-package --object-id status_glyph --role secondary --layer-kind icon-glyph --composition-order 30 --semantic-boundary "Foreground glyph separated from carrier tile." --asset status_glyph_rgba.png --mask status_glyph_source_mask.png --mask-source SAM2 --alpha-source "rembg refine" --tool-name SAM2 --tool-role segmentation --tool-version external --asset-class candidate --reuse-status draft-candidate
```

## Production Promotion

Promotion from draft candidate to production-ready requires:

- `metadata.capability.production_capable=true`
- mask overlay preview inspected
- alpha inspection preview inspected
- background residue check passed
- reuse readiness check passed
- user or manual acceptance recorded when the visual decision is subjective
- object `asset_class=atomic`
- object `reuse_status=production-ready`

If any of these are missing, keep `needs-review`, `blocked`, or `draft-candidate`.
