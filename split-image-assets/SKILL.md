---
name: split-image-assets
description: Use when turning a source image into a reusable production asset package with independent transparent PNG layers, masks, cleaned background, structured metadata, inspection previews, QA evidence, and manual-review flags. Use for image decomposition, asset splitting, sprite-sheet preview generation, mask/background asset packaging, and workflows where a 2x2 preview must not replace reusable assets.
---

# Split Image Assets

## Mission

Turn a source image into a reusable, inspectable asset package.

This skill is not a one-shot image prompt. Its main output is an asset package with transparent PNGs, masks, cleaned background, metadata, previews, and QA evidence. A 2x2 sprite sheet is only a preview artifact.

This skill is not a professional segmenter. It does not promise production-grade automatic segmentation by itself. Its job is to receive, normalize, inspect, package, and validate results from professional upstream tools or manual workflows. If mature upstream extraction is unavailable, the run must stay in draft-only packaging rather than claiming production extraction.

Structure the work as three layers: capability preparation, segmentation execution adapter, and quality adjudication. Capability preparation decides whether the run can be production-capable. The execution adapter normalizes professional upstream outputs into package-owned assets, masks, and provenance. Quality adjudication separates structural validation from visual quality warnings, user/manual acceptance, and production reuse claims.

Before extraction, explicitly state the quality target tier for the run:

- `structural-valid`: package contract, provenance, previews, and evidence are complete
- `usable-draft`: candidate assets are organized and reviewable, but not yet signoff-ready
- `visual-acceptance-ready`: current assets are intended to support final visual acceptance

## Iron Rules

```text
ANALYZE BEFORE EXTRACTING
EXTRACTION CAPABILITY GATE
PREFLIGHT TOOLING RECOMMENDATION GATE
DO NOT START EXTRACTION BEFORE TOOLING PREFLIGHT IS REPORTED AND RECORDED
GRANULARITY ALIGNMENT GATE
CONFIRMATION GATE
PROFESSIONAL SEGMENTER FIRST
SEMANTIC LAYERS BEFORE RECTANGLES
QUALITY-GATED PIPELINE
DECISION SYNC BEFORE AMBIGUOUS SPLITS
DO NOT DEFAULT TO ONE-PASS EXTRACTION
REUSABLE ASSETS BEFORE PREVIEWS
TRANSPARENT PNGS ARE PRODUCTION ASSETS
SOURCE-SPACE MASKS ARE NORMAL
STAGE INTERMEDIATES
PREVIEWS ARE INSPECTION ARTIFACTS
NEVER HIDE UNCERTAINTY
```

## Workflow

1. Read `references/workflow.md`.
2. Create or inspect the package directory.
3. Initialize the package with `scripts/init_asset_package.py` when a package does not already exist.
4. Run the Preflight Tooling Recommendation Gate before selecting a recipe or starting extraction:
   - run `scripts/check_extraction_environment.py`
   - report `segmentation`, `matting`, `reconstruction`, `environment`, `production_capable`, `missing_for_production`, `missing_roles`, `recommended_installs`, and `why_it_matters`
   - distinguish installed tooling, runtime-ready tooling, and production-ready capability
   - explain which missing upstream roles affect the run: detection, segmentation, alpha refinement/matting, and background reconstruction
   - proactively recommend installing or activating missing professional upstream tools
   - ask whether to continue with `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`
   - record the decision in `metadata.capability`, `metadata.confirmation.tooling_preflight`, and `metadata.decision_log[]`
   - do not continue into extraction until this decision is recorded
5. Read `references/pipeline-recipes.md` and `references/grounded-sam-pipeline.md` and select an extraction recipe before extraction.
6. Run the Granularity Alignment Gate before cutting pixels:
   - module-level, component-level, atomic-layer, or production-editable reconstruction
   - high-signal subset or full-image batch strategy
   - text/labels/buttons extracted as images or rebuilt downstream as live text/UI
   - carrier/glyph split, grouping, or conditional policy
   - exact background recovery required or approximate `background_clean.png` accepted as `needs-review`
   - animation-ready independent layers required or static reuse enough
7. For complex UI or graphic compositions, start with a high-signal subset instead of trying to atomize the entire image at once. Good first-pass targets are logos, nav icons, status dots, pins, checkboxes, chart marks, badges, and other small foreground elements whose masks can be inspected clearly.
   - for complex UI, run a pilot object first and stop for confirmation unless the pilot gate is explicitly recorded as `not-required`
8. For UI, dashboard, badge, tile/glyph, or dense interface images, read `references/ui-atomic-split.md` and create a semantic split plan before extraction.
   - classify each target as `ui-carrier`, `ui-glyph`, `carrier-glyph-pair`, `soft-edge-logo-brand-mark`, `outlined-illustration-logo`, `flat-support-plate`, or `photo-object-matte`
   - choose the upstream orchestration and repair path from that object type before cutting pixels
9. Analyze the source image before extraction:
   - visual hierarchy from background to foreground
   - main object
   - secondary objects
   - background type
   - occlusion
   - complex edges
   - transparent, reflective, fuzzy, smoky, or low-contrast regions
   - recommended split plan
10. When UI elements combine a carrier shape and a symbol, split them as tile/badge/panel background plus foreground glyph/symbol when independent reuse or clean edge review matters.
11. When the split plan has an ambiguous decision point or a subjective reuse boundary, run the Confirmation Gate before extracting. Read `references/confirmation-prompts.md` for grill-me style prompt templates.
   - the default is to stop and align with the user
12. Read `references/asset-package-contract.md` and update `metadata.json` with the visual hierarchy, recommended split plan, `extraction_pipeline`, and object inventory.
   - record `metadata.granularity.mode`, `metadata.granularity.user_confirmed`, and `metadata.granularity.notes`
   - for UI or dense compositions, also record `metadata.granularity.scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, and `layer_independence`
   - record object `asset_class` and `reuse_status` so draft candidates, support layers, and production-ready atomic assets cannot be confused
13. Produce or collect reusable assets:
   - transparent PNGs for individual objects
   - source-space masks
   - cleaned background
   - optional shadows and grouped object layers
   - for UI carriers, use `scripts/generate_ui_carrier_candidates.py` when reconstruction candidates are needed
   - for hard-edge UI glyphs, use `scripts/generate_ui_glyph_cleanup_candidates.py` when cleanup variants are needed
   - for small assets under roughly 128 px, prefer `scripts/upscale_repair_downscale.py` before final cleanup when quality matters
   - use `scripts/score_candidate_assets.py` before compare when candidate count or quality variance is high
14. Put external model outputs, candidate masks, refinement files, and temporary manifests in `_staging/` while active, then `_archive_intermediate/` when retained for traceability.
   - use `scripts/archive_intermediates.py` when you want a deterministic archive step
15. Normalize professional upstream results with `scripts/import_external_assets.py`. Treat this as the default production path:
   - professional upstream
   - `scripts/import_external_assets.py`
   - `scripts/build_previews.py`
   - `scripts/build_quality_previews.py`
   - `scripts/record_quality_review.py`
   - `scripts/validate_asset_package.py`
   - `scripts/export_asset_manifest.py`
16. Record per-layer segmentation quality evidence: semantic boundary, mask source, alpha source, edge checks, background residue checks, and reuse readiness.
17. Use `scripts/record_quality_review.py` to record semantic analysis, quality gates, object quality checks, and manual QA status after inspection instead of hand-editing JSON.
18. Build inspection previews with `scripts/build_previews.py`.
19. Build segmentation-quality previews with `scripts/build_quality_previews.py`.
20. Run `scripts/audit_visual_quality.py` for warning-only checks such as hard alpha edges, loose crops, large masks, and support plates miscounted as atomic assets.
21. Read `references/qa-standards.md` and inspect the package.
22. Validate structure with `scripts/validate_asset_package.py`.
23. Export a downstream layer manifest with `scripts/export_asset_manifest.py` after validation.
24. Read `references/manual-review.md` before assigning `pass`, `needs-review`, or `blocked`.

## Script Boundaries

The bundled scripts are deterministic packaging helpers. They do not perform segmentation, matting, inpainting, object recognition, or AI image generation.

Use external image tools, AI image editing, manual editing, or user-provided cutouts for the actual extraction work. Good default pipelines are Grounded-SAM/SAM2 style detection and segmentation, matting refinement with rembg/BiRefNet/RMBG-style tools, inpainting or manual paint repair for hidden background, and Qwen-Image-Layered style RGBA layer proposals when the source is a designed composition. Then use this skill to keep the package structure, previews, metadata, and QA evidence consistent.

Pillow, OpenCV, and skimage are not primary segmenters for production splitting. Use them for alpha compositing, PNG writing, source-space mask persistence, repair/refinement helpers, preview generation, metadata, and manifest packaging. Do not silently downgrade a production request to bbox or coordinate crops when the mature segmenter path is missing.

`scripts/import_external_assets.py` is the standard adapter for professional upstream outputs. Use it to copy SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual, or user-provided assets into the package while recording object metadata and upstream tool provenance. This adapter path is the primary production workflow, not a side path.

`scripts/check_extraction_environment.py` is the preflight tooling recommendation gate. It checks optional module presence, runtime readiness, and production-ready capability for segmentation, matting, reconstruction, and environment support. It does not install anything. For reconstruction, runtime support such as `torch` or `onnxruntime` is not enough by itself; only a dedicated reconstruction tool path should count as `production_ready=true`. Use the report to decide whether to run a local mature pipeline, request external assets, or continue as draft-packaging-only.

The capability report distinguishes module-installed from runtime-ready from production-ready states, lists `missing_for_production`, `missing_roles`, `recommended_installs`, and `why_it_matters`, and explains missing upstream role impact so an agent does not confuse partial local tooling with production readiness. `manual_redraw_path` is a human workflow, not automatic runtime capability, and should lead to `manual redraw required` or `approximate reconstruction only`, not to `production_capable=true`.

`scripts/build_quality_previews.py` creates QA evidence images such as mask overlays and alpha inspection previews. These previews are inspection artifacts; they do not upgrade a package to `pass` by themselves.

`scripts/audit_visual_quality.py` creates `_staging/quality/quality_audit.json` and `_staging/quality/qa_audit_contact_sheet.png`. It is a warning-only visual audit for risks such as `edge-halo`, `color-residue`, `detached-fragments`, `smear-artifact`, `over-flat-reconstruction`, `style-mismatch-reconstruction`, `hard-alpha-risk`, `support-layer-misclassified`, and `carrier-glyph-cross-contamination`. It does not replace manual review and does not set `qa.status=pass`.

`scripts/record_quality_review.py` is the standard manual-review adapter. Use it to write `metadata.analysis`, append `metadata.extraction_pipeline.quality_gates`, update per-object `quality_checks`, set `metadata.qa.status`, and append `qa_report.md` notes after inspection. It refuses `qa.status=pass` unless every required object quality check is `pass`.

`scripts/export_asset_manifest.py` creates `asset_manifest.json` for downstream renderers, animation pipelines, design tools, or manual review. It records package-relative asset paths sorted by `composition_order`; it does not validate visual quality or replace `metadata.json`.

`scripts/archive_intermediates.py` moves active `_staging/` outputs into `_archive_intermediate/<run-id>/`, writes an `archive_manifest.json` for traceability, and rewrites `metadata.audit.quality_audit_path` / `previews.qa_audit_contact_sheet` when those audit artifacts are archived.

`scripts/compare_candidate_assets.py` is the standard compare helper for high-risk repairs. Use it to turn staged repair candidates into a compare artifact plus metadata evidence before promotion.

`scripts/promote_candidate_asset.py` is the deterministic promotion helper for high-risk repairs. Use it when `_staging/repair_candidates/` contains multiple staged candidate assets and one should become the current package-owned asset without hand-editing `metadata.json`. Candidate promotion should come from `_staging/repair_candidates/`, not an arbitrary package path.

## Pipeline Quality Rule

Every reusable layer must have provenance. Record which tool or manual process created the mask, which process created or refined alpha, which stage repaired the background, the layer's `composition_order`, and which quality gates were inspected.

Every object layer must also declare `asset_class` and `reuse_status`. Use `asset_class=atomic` plus `reuse_status=production-ready` only for inspected reusable assets. Use `candidate` plus `draft-candidate` for imported or unreviewed upstream results. Use `grouped-support`, `background-support`, or `preview-reference` plus `support-only` for plates, grouped UI chrome, backgrounds, contact sheets, and other support/reference layers.

Every object layer must also declare `object_type`, `delivery_class`, `current_asset_revision`, and when relevant `selected_candidate_id`, `repair_history[]`, `candidate_comparisons[]`, and `active_reconstruction_method`. This keeps the current promoted asset distinct from rejected or archived repair candidates and forces UI/logo assets onto the right repair path.

Record the split decision that governed the run. `metadata.granularity` is required so future agents can see whether the package was aligned to module, component, atomic-layer, production-editable, or draft expectations and whether the user confirmed that scope.

Record the quality target that governed the run. `metadata.quality_target.tier` should stay aligned to `structural-valid`, `usable-draft`, or `visual-acceptance-ready`, and `qa.status=pass` requires `visual-acceptance-ready`.

For UI and dense compositions, do not batch-extract the full image before granularity scope is explicitly confirmed or clearly derivable from prior user instructions. Record the high-signal subset strategy, text handling, carrier/glyph policy, background expectation, and layer independence inside `metadata.granularity`.

Record the tooling preflight decision that governed the run. `metadata.capability` is required so future agents can see whether the run was production-capable, what upstream roles/tools were missing, which user choice was made, and why missing tools affect quality. `qa.status=pass` requires `metadata.capability.production_capable=true`; draft-only or unrecorded tooling preflight must stay `needs-review` or `blocked`.

Draft-only packages must not look production-complete. Mark unreviewed cutouts as draft candidates, mark plates and `background_clean` as support-only when appropriate, and report production-ready assets separately from draft candidate assets and support-only layers.

The validator checks evidence, not aesthetics. A package can pass structural validation only when it records `metadata.extraction_pipeline`, ordered stages, structured upstream tools, quality gates, object-level `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`, plus generated inspection previews and segmentation-quality previews for every reusable object layer.

Do not set `qa.status` to `pass` when any required object quality check is `needs-review`, `blocked`, or `unknown`.

## Semantic Layer Rule

Do not treat rectangular crops as asset splitting. A package with only page regions, grid cells, or convenient bounding boxes is not complete even when every crop has an alpha channel.

First identify the image's semantic layer hierarchy: background/backplate, frame or chrome, primary subjects, secondary objects, connection layers, labels, buttons or controls, shadows, and decorative details. Extract or reconstruct those layers separately. Use a rectangle only as the storage bbox around a semantic mask, never as the reason an asset exists.

If the hidden background cannot be recovered from one flattened image, create an honest `background_clean.png` approximation or leave the package `needs-review`/`blocked`; do not claim exact recovery.

Pillow crops, bbox masks, manual-estimated crop masks, or coordinate-only cuts are draft evidence by default. They cannot support `qa.status=pass` unless a human has confirmed the crop-only layer through `record_quality_review.py --confirm-crop-layer` and the object records `manual_review_confirmed=true`.

Likewise, helper-only extraction sources such as Pillow crop alpha, OpenCV threshold masks, or skimage thresholding cannot support `qa.status=pass` on their own unless a human explicitly confirms that layer.

Background clean plates, support plates, grouped structural UI regions, and inpainted/reconstructed areas may be useful deliverables, but they must be marked approximate when they are approximate and must record `reconstruction_provenance`. Keep them `needs-review` unless a human explicitly accepts that layer.

Approximate reconstructed carriers or clean plates should use `delivery_class=approximate-reconstruction`. Do not hide them inside `production-ready` naming or counts.

Source-space masks are expected: `masks/*.png` should normally match the original source dimensions for overlay QA and provenance tracing. A black mask with a small white component is valid when the object is small. Store the tight reusable visual result in `assets/*.png`; store the full-source QA mask in `masks/*.png`.

## Decision Sync Rule

Use these formal confirmation gates instead of vague “ask when needed” behavior:

- `Granularity Alignment Gate`
  - Trigger: complex UI, dashboard, dense composition, or any run where split scope affects reuse boundaries.
  - Ask: “Should this package target component-level, atomic-layer, or production-editable reconstruction?”
  - Recommended answer: `atomic-layer` for reusable UI atoms; `production-editable` when downstream rebuild matters.
  - Metadata effect: update `metadata.granularity.mode`, `scope_strategy`, `text_handling`, `background_expectation`, and `layer_independence`.
- `Carrier/Glyph Split Gate`
  - Trigger: icon-in-tile, badge-in-card, glyph-on-plate, or any `carrier-glyph-pair`.
  - Ask: “Should this carrier and glyph stay grouped, or split into separate reusable layers?”
  - Recommended answer: `split` unless the grouped layer is explicitly the downstream requirement.
  - Metadata effect: update `metadata.granularity.carrier_glyph_policy` and record the decision in `metadata.decision_log[]`.
- `Approximate Reconstruction Acceptance Gate`
  - Trigger: background/carrier repair requires inferred pixels or manual redraw.
  - Ask: “Is an approximate reconstructed layer acceptable for this package?”
  - Recommended answer: yes only when the layer can stay `needs-review` or is explicitly accepted for the target use.
  - Metadata effect: keep `delivery_class=approximate-reconstruction`, record `reconstruction_provenance`, `active_reconstruction_method`, and a reconstruction acceptance decision in `metadata.decision_log[]`.
  - Required wording before promotion: `This is still approximate because hidden pixels are inferred.`
- `Final Promotion Acceptance Gate`
  - Trigger: a candidate is about to replace the current asset revision.
  - Ask: “Should candidate X become the current revision for this object?”
  - Recommended answer: yes only after compare evidence or a direct-promotion rationale exists.
  - Metadata effect: update `selected_candidate_id`, `current_asset_revision`, `repair_history[]`, `candidate_comparisons[]`, and the QA report.

When a split decision affects reuse boundaries, editability, animation readiness, localization, approximate reconstruction acceptance, or final delivery claims, pause and run a one-question confirmation step before continuing that branch.

This is a confirmation-driven workflow, not passive ambiguity handling. Ask one question at a time, include the recommended answer, resolve one branch before moving on, and inspect the source image, metadata, and prior user instructions before asking. Do not batch unrelated questions unless the user explicitly asks for a full alignment round.

Ask when deciding:

- whether a visually connected region should stay grouped or become separate reusable layers
- whether labels, buttons, text, or UI chrome should be extracted as images or rebuilt downstream
- whether uncertain edges, hidden background, or reconstructed pixels can be accepted as `needs-review`
- whether to prefer exact source preservation, editable layers, animation-ready layers, or quick draft assets
- whether a low-confidence automated mask should be retried with another upstream tool or sent to manual review
- whether structurally valid output should remain `needs-review` until the user accepts its cleanliness and granularity
- whether a warning is a true defect, an expected stylistic signal, or mixed and needs human judgment

If the answer can be determined from the source image, existing metadata, or user-provided requirements, inspect that evidence first. If ambiguity remains, ask exactly one focused question and wait for the answer before continuing that branch.

Record confirmation outcomes in `metadata.decision_log[]` with `stage`, `question`, `recommended_answer`, `user_answer`, `decision_effect`, and `decision_source`. For the hard workflow gates, also update `metadata.confirmation`.

## Reference Routing

- Read `references/workflow.md` for the full staged workflow.
- Read `references/pipeline-recipes.md` before choosing or documenting the extraction path.
- Read `references/grounded-sam-pipeline.md` before accepting or running professional upstream outputs.
- Read `references/ui-atomic-split.md` before planning complex UI, dashboard, badge, tile/glyph, or control-heavy images.
- Read `references/asset-package-contract.md` before creating, renaming, or validating files.
- Read `references/qa-standards.md` before claiming an asset is reusable.
- Read `references/manual-review.md` when confidence is low, edges are complex, objects overlap, or background repair is uncertain.
- Read `references/confirmation-prompts.md` when a decision needs user confirmation or should be recorded from prior instructions.

## Output Expectations

At minimum report:

- package path
- source image
- tooling preflight result
- production_capable: true/false
- missing upstream roles/tools
- user choice: install/activate tools, external professional outputs, or draft-packaging-only
- quality implication of missing tools
- quality target tier and why it is not higher yet
- granularity mode, whether it was user-confirmed or inferred, split scope notes, and whether text/UI chrome is extracted or rebuilt downstream
- object types and the chosen upstream orchestration per type
- confirmation decisions recorded in `metadata.decision_log`
- visual hierarchy and recommended split plan
- extraction pipeline recipe, stages, upstream tools, and quality gates
- primary segmenter, matting tool, and helper tools
- asset_class/reuse_status policy used for this run
- object inventory
- generated or collected assets
- previews
- quality preview evidence
- visual quality audit result and warning count
- downstream asset manifest
- validation result: structural package valid or structurally invalid
- visual quality result: pass, needs-review, or blocked
- production-ready assets
- draft candidate assets
- support-only layers
- QA status: `pass`, `needs-review`, or `blocked`
- manual-review flags and next correction points
