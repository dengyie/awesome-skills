# Split Image Assets Workflow

## Purpose

Use this workflow to turn a single source image into a reusable asset package. Optimize for reusable files, clear provenance, inspectable previews, and honest QA status.

The normal production path is professional upstream extraction -> package import -> preview evidence -> QA review -> validation -> manifest export. This workflow should make professional results auditable and deliverable; it should not pretend to replace the upstream segmenter.

Keep the workflow split into three layers:

- capability preparation: decide whether the run is production-capable or draft-packaging-only
- segmentation execution adapter: run or receive professional upstream outputs and import them into the package contract
- quality adjudication: inspect evidence, run warning-only audits, record review outcomes, validate structure, and separate draft candidates from production-ready assets

## Stages

1. Intake the source image and identify the desired output package directory.
2. Run `scripts/init_asset_package.py` if the package does not already exist.
3. Run the Preflight Tooling Recommendation Gate before extraction:
   - run `scripts/check_extraction_environment.py`
   - require a report that includes `segmentation`, `matting`, `reconstruction`, `environment`, `production_capable`, and `missing_for_production`
   - distinguish installed tooling from runtime-ready and production-ready capability
   - explicitly classify the run as `production-capable` or `draft-packaging-only`
   - explain which missing upstream roles affect the run: detection, segmentation, alpha refinement/matting, and background reconstruction
   - proactively recommend installing or activating missing professional upstream tools
   - ask whether to continue with `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`
   - record the decision in `metadata.capability` and `metadata.decision_log[]`
   - do not continue into extraction until this decision is recorded
4. Read `pipeline-recipes.md` and `grounded-sam-pipeline.md` and choose a pipeline recipe.
5. Run the Granularity Confirmation Gate before extraction:
   - choose module-level, component-level, atomic-layer, or production-editable reconstruction
   - choose `high-signal-subset` or `full-image-batch` scope strategy
   - decide whether text, labels, buttons, and UI chrome become image assets or live downstream elements
   - decide whether carrier/glyph structures should split, stay grouped, or remain conditional pending review
   - decide whether approximate background repair is acceptable or exact recovery is required
   - decide whether layers must be animation-ready or static-reuse ready
6. Run the Semantic Split Plan Confirmation Gate when layer boundaries, grouping, carrier/glyph separation, or text ownership are subjective.
7. Choose a high-signal first subset when the image is complex. For flat UI and dashboards, start with logos, nav icons, status dots, pins, checkboxes, chart marks, badges, and other small foreground elements that a professional segmenter can isolate and a reviewer can inspect clearly.
8. For UI, dashboard, badge, tile/glyph, control-heavy, or dense interface images, read `ui-atomic-split.md` and create a layer plan that marks each expected layer as `must_extract`, `rebuild_downstream`, `support_only`, `skip_for_now`, or `requires_user_confirmation`.
9. Analyze before extraction:
   - source dimensions
   - semantic layer hierarchy from background to foreground
   - main object
   - secondary objects
   - background type
   - object overlap
   - shadows
   - complex edge regions
   - likely manual-review risks
10. For UI icon-in-tile, badge-in-card, and glyph-on-plate patterns, prefer separate carrier and glyph layers when that makes reuse or mask cleanup clearer.
11. Run the Low-Confidence Mask Handling Gate when a mask should be retried, manually reviewed, or retained as draft-only.
12. Run the Approximate Reconstruction Acceptance Gate before treating background clean plates or support plates as acceptable.
13. Write `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `granularity`, `capability`, `decision_log`, `extraction_pipeline`, object `asset_class`, object `reuse_status`, and the object inventory into `metadata.json`.
   - for UI or dense compositions, record `granularity.scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, and `layer_independence`
14. Produce or collect reusable assets through AI image tools, segmentation tools, manual editing, or user-provided files. Use professional segmentation or matting as the primary extraction path; Pillow/OpenCV/skimage are helper tools for compositing, refinement, previews, and packaging.
15. Keep active external outputs, candidate masks, and temporary manifests in `_staging/`. Move retained intermediate evidence to `_archive_intermediate/` before final validation, preferably through `scripts/archive_intermediates.py`, which should also keep audit metadata paths synchronized when `_staging/quality/` is archived.
16. Normalize external outputs with `scripts/import_external_assets.py` when assets come from SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual editing, or user-provided files. Imported objects default to `asset_class=candidate` and `reuse_status=draft-candidate`.
17. Record composition order, mask source, alpha source, semantic boundary, asset class, reuse status, and object-level quality checks for every reusable layer. Use `scripts/record_quality_review.py` after inspection so semantic analysis, quality gates, QA status, `decision_log`, and `qa_report.md` stay synchronized.
18. Keep individual objects separate before creating grouped or preview outputs. Grouped convenience layers should be marked `grouped-support` or `support-only`.
19. Generate previews with `scripts/build_previews.py`.
20. Generate segmentation-quality previews with `scripts/build_quality_previews.py`.
21. Run `scripts/audit_visual_quality.py` to create warning-only `_staging/quality/quality_audit.json` and `_staging/quality/qa_audit_contact_sheet.png` evidence before final review.
22. Inspect previews and audit warnings, then update object quality checks and QA status with `scripts/record_quality_review.py` when appropriate.
23. For high-risk repairs, write candidate outputs into `_staging/repair_candidates/`, compare at least two candidates when available, and promote the selected candidate with `scripts/promote_candidate_asset.py` instead of overwriting `assets/` by hand. Do not promote from an arbitrary package path.
24. Use `scripts/compare_candidate_assets.py` before promotion when more than one viable repair candidate exists. The compare artifact is review evidence, not a final asset, and should stay in `_staging/repair_candidates/` or `_archive_intermediate/`.
25. Run the Final User Acceptance Gate before promoting subjective visual decomposition to `qa.status=pass`. If the user has not accepted the current granularity and cleanliness, keep `needs-review` even when validation passes.
26. Validate the package with `scripts/validate_asset_package.py`.
27. Export a downstream layer manifest with `scripts/export_asset_manifest.py`.
28. Report structural validation separately from visual quality status, plus production-ready, draft-candidate, support-only, and blocked counts.

## Standard Failure Outputs

Use stable outcome language when the workflow cannot claim production extraction:

- `blocked: missing professional segmentation capability`
- `needs-review: imported upstream assets require QA`
- `draft-only: package initialized without production extraction claim`
  - must say `not production reusable`
  - should report `production-ready assets: 0` unless production-capable upstream evidence and review promotion exist

## Status Meanings

- `pass`: structure is valid and inspection found no blocking reuse issue.
- `needs-review`: package is usable as a draft, but one or more assets need human inspection or correction.
- `blocked`: package cannot be treated as reusable until missing files or serious quality issues are resolved.

## Do Not

- Do not treat a 2x2 preview as the final asset.
- Do not treat rectangular crops, grid slices, or page regions as assets unless each crop is only a tight bbox around a semantic mask.
- Do not promote bbox/manual-estimated crop layers to `pass` without explicit per-layer human confirmation.
- Do not merge separate objects into one layer unless the grouped layer is explicitly additional.
- Do not hide AI-assisted fills or uncertain edges.
- Do not claim the scripts extracted objects from the source image.
- Do not start extraction before reporting missing professional upstream capabilities and recording whether the user chose installation/activation, external professional outputs, or draft-packaging-only.
- Do not claim segmentation quality when `extraction_pipeline` or per-object quality evidence is missing.
- Do not leave external model folders or temporary manifests in the package root; use `_staging/` or `_archive_intermediate/`.
- Do not mark approximate background or structural reconstruction as exact extraction.
- Do not silently choose split granularity, grouping boundaries, approximate reconstruction acceptance, or final QA acceptance when those decisions materially affect downstream reuse.
- Do not default to one-pass extraction when reuse boundaries are subjective.
- Do not batch-extract dense UI before granularity scope and carrier/glyph policy are explicitly confirmed or clearly derivable from prior instructions.

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

For UI assets, check whether a tile, badge, or panel background should be split from its foreground glyph or symbol. This is often cleaner than one mixed layer because SAM-style masks can merge the carrier shape and glyph.

## User Decision Sync

When a split choice affects future reuse, editing, localization, animation, approximate reconstruction acceptance, final delivery claims, or visual truth, ask the user one focused question before continuing. Include your recommended answer. Do not batch multiple questions unless the user asks for a full grill-me style interrogation.

Record each confirmation in `metadata.decision_log[]`. If prior instructions or metadata already answer the question, record the decision instead of asking again.

## Tooling Preflight

Before extraction, tell the user what the environment can and cannot support. Missing SAM2 or a grounded detector means object boundaries may need manual prompts or may be less reliable. Missing rembg/BiRefNet/RMBG-style matting means transparent PNG alpha edges may keep halos, dark fringes, or background residue. Missing inpainting or a manual repair path means `background_clean.png` can only be approximate or `needs-review`.

Record the outcome in `metadata.capability`:

- `production_capable`
- `missing_for_production`
- `user_choice`: `install-or-activate-tools`, `external-professional-outputs`, `draft-packaging-only`, or `production-capable`
- `notes`

When the user chooses `draft-packaging-only`, keep `qa.status=needs-review` or `blocked`.

## Quality-Gated Pipeline Checklist

Before claiming reuse quality, record:

- selected recipe such as `grounded-segmentation-matting-repair` or `layered-rgba-decomposition`
- ordered stages from semantic analysis through QA review
- upstream tools and manual operations used for masks, alpha, background repair, and layer proposals
- primary segmenter, matting tool, and helper tools used in the run summary
- tooling preflight result, missing upstream roles, user choice, and quality implications
- quality gates inspected for mask alignment, alpha edges, background residue, and reuse readiness
- recorded granularity mode and whether the user confirmed it
- object-level `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, `asset_class`, `reuse_status`, and `quality_checks`
- warning-only visual audit result from `scripts/audit_visual_quality.py`

## Downstream Manifest

Run `scripts/export_asset_manifest.py` after validation when another tool needs a stable layer list. The script writes `asset_manifest.json` by default, sorted by `composition_order`, with package-relative asset and mask paths plus quality status per layer.

The manifest is a consumer-facing index. It does not replace `metadata.json`, `qa_report.md`, or manual inspection.

## Final Report Shape

Use this language so structural package validity is not mistaken for production visual quality:

```text
Validation result: structural package valid / structurally invalid
Visual quality result: pass / needs-review / blocked
Production reusable assets: N
Draft candidate assets: N
Support-only layers: N
Blocked assets: N
Not production reusable: yes/no
```

Also list:

- expected semantic layers
- extracted layers
- missing layers
- grouped-but-not-atomic layers
- layers requiring downstream rebuild
- approximate layers
