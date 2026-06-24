# Split Image Assets

Use `split-image-assets` when a source image needs to become a reusable asset package instead of a single preview image.

The skill helps produce transparent PNG object layers, mask files, `background_clean.png`, `metadata.json`, `qa_report.md`, and inspection previews such as `sprite_sheet_2x2.png`.

The deterministic script layer does not perform segmentation. Use AI image editing, segmentation tools, manual editing, or user-provided cutouts to create object assets, then use the scripts to initialize, preview, and validate the package.

The default production path is professional upstream -> import -> preview -> QA review -> validate -> manifest. This skill is the workflow, packaging, and QA tail of that chain; it is not the upstream segmenter.

For quality-first extraction, use a Grounded-SAM/SAM2 style pipeline: semantic analysis, text-guided detection, segmentation, alpha refinement with rembg/BiRefNet/RMBG-style tools, background repair with inpainting or manual paint work, then QA. For layer-first decomposition, use Qwen-Image-Layered style RGBA layer proposals, then inspect every layer before treating it as production-ready.

Start by recording a semantic layer hierarchy in `metadata.analysis.visual_hierarchy`. Split by meaning: background/backplate, frame or UI chrome, main subjects, connection paths, labels, buttons, decorations, shadows, and overlays. A rectangular crop is only acceptable as a tight storage bbox around a semantic mask; rectangular crop packages are not complete asset packages.

## Before extraction

Run the Preflight Tooling Recommendation Gate before starting a high-quality split:

```bash
python split-image-assets/scripts/check_extraction_environment.py
```

If mature segmentation/matting tools are unavailable and no external masks or cutouts were provided, do not claim production extraction. Explain which upstream role is missing, what quality it affects, and ask whether to install or activate tools, provide external professional split outputs, or continue as draft-packaging-only.

Always report whether the run is `production-capable` or `draft-packaging-only`. If it is not production-capable, explicitly list what is missing, record the user choice in `metadata.capability`, and keep the package honest.

Missing upstream role examples:

- missing SAM2 or grounded detector: object boundaries may need manual prompts or may be less reliable
- missing rembg/BiRefNet/RMBG: alpha edges may keep halos, dark fringes, or background residue
- missing inpainting/manual repair path: `background_clean.png` can only be approximate or `needs-review`

Also align split granularity before cutting pixels: module-level, component-level, atomic-layer, or production-editable reconstruction; text as image assets or live downstream text; exact background recovery or approximate `background_clean.png`; animation-ready layers or static reuse.

When granularity, carrier/glyph grouping, text ownership, approximate background acceptance, low-confidence masks, or final `pass` claims are subjective, use a grill-me style confirmation step: ask one focused question, include your recommended answer, resolve that branch, then record the outcome in `metadata.decision_log[]`. If prior instructions already answer the question, record the decision instead of asking again.

Use a professional segmenter or matting pipeline as the primary source for production masks. Pillow, OpenCV, and skimage are helpers for alpha compositing, source-space mask persistence, preview generation, repair, and packaging; they are not a substitute for SAM2/SAM/Grounded-SAM/rembg/BiRefNet/RMBG-style extraction.

For complex UI screenshots, start with a high-signal subset such as logo, nav icon, status dot, pin, checkbox, chart mark, badge, or row glyph. For icon-in-tile or glyph-on-plate elements, split the tile/badge/panel background from the foreground glyph when reuse or edge cleanup benefits from separate layers.

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
  _staging/
  _archive_intermediate/
```

`metadata.json` must also include `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `extraction_pipeline`, and per-object quality evidence so reviewers can tell whether extraction followed the image structure instead of only cutting page regions.
It should also record `granularity.mode`, `granularity.user_confirmed`, `granularity.notes`, `capability.production_capable`, `capability.missing_for_production`, `capability.user_choice`, `capability.notes`, and `decision_log[]` so later agents can see what split scope, tooling capability, and subjective decisions were agreed.

`assets/*.png` are reusable transparent layers. `masks/*.png` are source-space QA masks aligned to the original image, so a small object may appear as a small white region on a mostly black mask. Put active external model outputs, candidate masks, and temporary manifests in `_staging/`; move retained evidence to `_archive_intermediate/` before final validation.

## Basic Commands

```bash
python split-image-assets/scripts/check_extraction_environment.py
python split-image-assets/scripts/init_asset_package.py source.png output-package
python split-image-assets/scripts/import_external_assets.py output-package --object-id main_object --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject from SAM2 mask" --asset main.png --mask mask_main.png --mask-source sam2 --alpha-source rembg --tool-name SAM2 --tool-role segmentation --tool-version external
python split-image-assets/scripts/build_previews.py output-package
python split-image-assets/scripts/build_quality_previews.py output-package
python split-image-assets/scripts/record_quality_review.py output-package --production-capable true --capability-user-choice production-capable --capability-note "SAM2 and rembg-style external outputs were provided." --visual-hierarchy background --visual-hierarchy "main object" --recommended-split-plan "Keep the main object separate from the background." --granularity-mode atomic-layer --granularity-confirmed --granularity-note "Atomic foreground layers; text rebuilt downstream." --decision-stage tooling-preflight --decision-question "Install tools, provide external outputs, or continue draft-only?" --decision-recommended "Install/provide SAM2 or Grounded-SAM plus rembg/BiRefNet/RMBG for production-quality extraction." --decision-answer "external professional outputs provided" --decision-effect "Use imported professional outputs and allow pass only after QA evidence passes." --quality-gate "mask overlay inspected" --object-id main_object --mask-alignment pass --alpha-edges pass --background-residue pass --reuse-readiness pass --qa-status pass --review-note "Manual inspection accepted the imported layer."
python split-image-assets/scripts/archive_intermediates.py output-package --run-id sam-pass-001
python split-image-assets/scripts/validate_asset_package.py output-package
python split-image-assets/scripts/export_asset_manifest.py output-package
```

`asset_manifest.json` is the downstream handoff file for renderers, animation tooling, design imports, or manual review queues. It is generated from `metadata.json`, sorted by `composition_order`, and uses package-relative paths.

## QA

Use `pass` only when reusable assets, masks, metadata, previews, and background repair are acceptable. Use `needs-review` when edge quality, AI-assisted regions, object roles, or background repair need manual review. Use `blocked` when required files are missing or the package cannot be reused safely.

A `draft-packaging-only` run cannot support `qa.status=pass`. Keep it `needs-review` or `blocked` unless production-capable upstream evidence or external professional outputs are recorded.

Use `needs-review` or `blocked` when the background is only a reconstructed approximation, when core layers are missing, or when the result is mostly rectangular crops.

Per-object `quality_checks` should cover mask alignment, alpha edges, background residue, and reuse readiness. Missing mask or alpha provenance is a review blocker even when the PNG file opens correctly. Record `composition_order` so downstream renderers can rebuild the layer stack, and do not set package `qa.status` to `pass` unless every required object quality check is `pass`.

Use `record_quality_review.py` after inspecting previews to update `metadata.json` and append `qa_report.md` together. This prevents the common failure where imported layers remain `needs-review`, semantic analysis is missing, or `qa.status` is promoted without matching object-level evidence.

Validation now requires both ordinary inspection previews from `build_previews.py` and quality previews from `build_quality_previews.py` for each reusable object layer. A package without preview evidence is incomplete even if the transparent PNGs and masks exist.

Bbox/manual-estimated crop layers are draft-only unless explicitly confirmed. Use `record_quality_review.py --confirm-crop-layer --object-id <id>` only after a human accepts that layer for production reuse.

Approximate `background_clean.png` files and structural support plates should record `reconstruction_provenance` and remain `needs-review` unless the approximation has been explicitly accepted.

When you summarize a run, call out the primary segmenter, the matting/refinement tool, and any helper-only tools separately. Pillow/OpenCV/skimage should only appear in the helper-tools bucket.
