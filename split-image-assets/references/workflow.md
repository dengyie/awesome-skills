# Split Image Assets Workflow

## Purpose

Use this workflow to turn a single source image into a reusable asset package. Optimize for reusable files, clear provenance, inspectable previews, and honest QA status.

The normal production path is professional upstream extraction -> package import -> preview evidence -> QA review -> validation -> manifest export. This workflow should make professional results auditable and deliverable; it should not pretend to replace the upstream segmenter.

Keep the workflow split into three layers:

- capability preparation: decide whether the run is production-capable or draft-packaging-only
- segmentation execution adapter: run or receive professional upstream outputs and import them into the package contract
- quality adjudication: inspect evidence, run warning-only audits, record review outcomes, validate structure, and separate draft candidates from production-ready assets

Declare the target quality tier before extraction starts:

- `structural-valid`
- `usable-draft`
- `visual-acceptance-ready`

Do not let `structural-valid` package success masquerade as `visual-acceptance-ready`.

## Interaction State Machine

Only three event classes may pause execution:

- `user-decision`
- `external-blocker`
- `formal-approval`

Everything else stays in `Running` and should be reported as commentary only. Progress updates do not create gate state and must not block execution.

Use these states consistently:

- `Running`
- `AwaitingDecision`
- `AwaitingExternalBlocker`
- `AwaitingApproval`
- `Completed`

## Stages

1. Intake the source image and identify the desired output package directory.
2. Run `scripts/init_asset_package.py` if the package does not already exist.
3. Run the Preflight Tooling Recommendation Gate before extraction:
   - Pause category: `external-blocker` by default, `user-decision` only when multiple valid user-selectable paths already exist
   - run `scripts/check_extraction_environment.py`
   - require a report that includes `segmentation`, `matting`, `reconstruction`, `environment`, `production_capable`, `missing_for_production`, `missing_roles`, `recommended_installs`, and `why_it_matters`
   - distinguish installed tooling from runtime-ready and production-ready capability
   - explicitly classify the run as `production-capable` or `draft-packaging-only`
   - explain which missing upstream roles affect the run: detection, segmentation, alpha refinement/matting, and background reconstruction
   - proactively recommend installing or activating missing professional upstream tools
   - ask whether to continue with `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`
   - record the decision in `metadata.capability`, `metadata.confirmation.tooling_preflight`, and `metadata.decision_log[]`
   - do not continue into extraction until this decision is recorded
4. Read `pipeline-recipes.md` and `grounded-sam-pipeline.md` and choose a pipeline recipe.
5. Run the Granularity Confirmation Gate before extraction.
   - Pause category: `user-decision`
   - choose module-level, component-level, atomic-layer, or production-editable reconstruction
   - choose `high-signal-subset` or `full-image-batch` scope strategy
   - decide whether text, labels, buttons, and UI chrome become image assets or live downstream elements
   - decide whether carrier/glyph structures should split, stay grouped, or remain conditional pending review
   - decide whether approximate background repair is acceptable or exact recovery is required
   - decide whether layers must be animation-ready or static-reuse ready
6. Run the Semantic Split Plan Confirmation Gate when layer boundaries, grouping, carrier/glyph separation, or text ownership are subjective.
   - `Granularity Alignment Gate`
     - Pause category: `user-decision`
     - Trigger: complex UI, dashboard, dense composition, or reuse-boundary ambiguity.
     - Ask: “Should this package target component-level, atomic-layer, or production-editable reconstruction?”
     - Recommended answer: `atomic-layer` for reusable UI assets; `production-editable` when downstream rebuild is required.
     - Metadata effect: record `mode`, `scope_strategy`, `text_handling`, `background_expectation`, `layer_independence`, `metadata.confirmation.granularity_alignment`, and a formal decision-log entry.
   - `Carrier/Glyph Split Gate`
     - Pause category: `user-decision`
     - Trigger: icon-in-tile, badge-in-card, glyph-on-plate, or `carrier-glyph-pair`.
     - Ask: “Should the carrier and glyph split into separate layers?”
     - Recommended answer: `split`.
     - Metadata effect: record `carrier_glyph_policy` and a decision-log entry.
   - `Approximate Reconstruction Acceptance Gate`
     - Pause category: `user-decision` first, `formal-approval` before claim escalation
     - Trigger: inferred pixels, manual redraw, or approximate carrier/background repair.
     - Ask: “Is approximate reconstruction acceptable for this layer?”
     - Recommended answer: only when approximate delivery is explicitly acceptable.
     - Metadata effect: keep `delivery_class=approximate-reconstruction`, record reconstruction provenance/method, `metadata.confirmation.approximate_reconstruction`, and a formal decision-log entry.
   - `Final Acceptance Gate`
     - Pause category: `formal-approval`
     - Trigger: the package is about to claim `qa.status=pass`, `visual-acceptance-ready`, or `production-ready`.
     - Ask: “Does the current package meet the requested granularity and cleanliness well enough to mark pass?”
     - Recommended answer: keep `needs-review` unless current boundaries, cleanliness, and approximations have actually been accepted.
     - Metadata effect: update `metadata.confirmation.final_acceptance` and a formal decision-log entry.
   - `Final Promotion Acceptance Gate`
     - Pause category: `formal-approval`
     - Trigger: a candidate is ready to replace the current revision.
     - Ask: “Should candidate X become the current revision?”
     - Recommended answer: only after compare evidence or a direct-promotion rationale exists.
     - Metadata effect: update `selected_candidate_id`, `current_asset_revision`, `repair_history[]`, `candidate_comparisons[]`, `metadata.confirmation.candidate_promotion`, and a formal decision-log entry.
7. Choose a high-signal first subset when the image is complex. For flat UI and dashboards, start with logos, nav icons, status dots, pins, checkboxes, chart marks, badges, and other small foreground elements that a professional segmenter can isolate and a reviewer can inspect clearly.
8. For UI, dashboard, badge, tile/glyph, control-heavy, or dense interface images, run the `Pilot Object Gate` before wider batch extraction.
   - Pause category: `formal-approval`
   - Record `metadata.confirmation.pilot_object` as `confirmed` or evidence-backed `not-required`.
9. For UI, dashboard, badge, tile/glyph, control-heavy, or dense interface images, read `ui-atomic-split.md` and create a layer plan that marks each expected layer as `must_extract`, `rebuild_downstream`, `support_only`, `skip_for_now`, or `requires_user_confirmation`.
10. Route each planned target by object type before extraction or repair:
   - `ui-carrier`
   - `ui-glyph`
   - `carrier-glyph-pair`
   - `soft-edge-logo-brand-mark`
   - `outlined-illustration-logo`
   - `flat-support-plate`
   - `photo-object-matte`
11. Use the routed object type to choose the upstream orchestration:
   - `carrier-glyph-pair`: grounded detection or SAM2 masks -> glyph/carrier split -> glyph exclusion dilation -> carrier reconstruction candidate generation -> glyph cleanup candidate generation -> candidate scoring -> compare -> promotion
   - `ui-carrier`: source crop + carrier mask + glyph mask -> `generate_ui_carrier_candidates.py` -> `score_candidate_assets.py` -> `compare_candidate_assets.py`
   - `ui-glyph`: isolated glyph + carrier/background estimate -> `generate_ui_glyph_cleanup_candidates.py` -> `score_candidate_assets.py` -> `compare_candidate_assets.py`
   - `soft-edge-logo-brand-mark` or `photo-object-matte`: professional segmentation + matting first, cleanup second
12. For small assets under roughly 128 px, prefer `upscale-repair-downscale.py` as an official prep/finalize path instead of ad hoc manual resampling.
13. Analyze before extraction:
   - source dimensions
   - semantic layer hierarchy from background to foreground
   - main object
   - secondary objects
   - background type
   - object overlap
   - shadows
   - complex edge regions
   - likely manual-review risks
14. For UI icon-in-tile, badge-in-card, and glyph-on-plate patterns, prefer separate carrier and glyph layers when that makes reuse or mask cleanup clearer.
15. Run the Low-Confidence Mask Handling Gate when a mask should be retried, manually reviewed, or retained as draft-only.
   - Pause category: `user-decision` only when the branch materially changes deliverable truth; otherwise keep progress in commentary and continue the chosen path.
16. Run the Approximate Reconstruction Acceptance Gate before treating background clean plates or support plates as acceptable.
17. Write `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `granularity`, `capability`, `quality_target`, `confirmation`, `decision_log`, `extraction_pipeline`, object `object_type`, object `asset_class`, object `reuse_status`, and the object inventory into `metadata.json`.
   - for UI or dense compositions, record `granularity.scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, and `layer_independence`
17. Produce or collect reusable assets through AI image tools, segmentation tools, manual editing, or user-provided files. Use professional segmentation or matting as the primary extraction path; Pillow/OpenCV/skimage are helper tools for compositing, refinement, previews, and packaging.
18. Keep active external outputs, candidate masks, and temporary manifests in `_staging/`. Move retained intermediate evidence to `_archive_intermediate/` before final validation, preferably through `scripts/archive_intermediates.py`, which should also keep audit metadata paths synchronized when `_staging/quality/` is archived.
19. Normalize external outputs with `scripts/import_external_assets.py` when assets come from SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual editing, or user-provided files. Imported objects default to `asset_class=candidate` and `reuse_status=draft-candidate`.
20. Record composition order, mask source, alpha source, semantic boundary, object type, asset class, reuse status, and object-level quality checks for every reusable layer. Use `scripts/record_quality_review.py` after inspection so semantic analysis, quality gates, QA status, `quality_target`, `decision_log`, and `qa_report.md` stay synchronized.
21. Keep individual objects separate before creating grouped or preview outputs. Grouped convenience layers should be marked `grouped-support` or `support-only`.
22. Generate previews with `scripts/build_previews.py`.
23. Generate segmentation-quality previews with `scripts/build_quality_previews.py`.
24. Run `scripts/audit_visual_quality.py` to create warning-only `_staging/quality/quality_audit.json` and `_staging/quality/qa_audit_contact_sheet.png` evidence before final review.
25. Inspect previews and audit warnings, then classify each warning as `true defect`, `expected stylistic signal`, or `mixed / needs human judgment` before “fixing” it.
26. For high-risk repairs, write candidate outputs into `_staging/repair_candidates/`, score them with `scripts/score_candidate_assets.py`, compare at least two viable candidates when available, and promote the selected candidate with `scripts/promote_candidate_asset.py` instead of overwriting `assets/` by hand. Do not promote from an arbitrary package path.
27. Use `scripts/compare_candidate_assets.py` before promotion when more than one viable repair candidate exists. The compare artifact is review evidence, not a final asset, and should stay in `_staging/repair_candidates/` or `_archive_intermediate/`. Treat compare as a structured evidence step, not just a screenshot.
28. Run the Final User Acceptance Gate before promoting subjective visual decomposition to `qa.status=pass`.
   - Pause category: `formal-approval`
   - If the user has not accepted the current granularity and cleanliness, keep `needs-review` even when validation passes.
29. Validate the package with `scripts/validate_asset_package.py`.
30. Export a downstream layer manifest with `scripts/export_asset_manifest.py`.
31. Report structural validation separately from visual quality status, plus production-ready, draft-candidate, support-only, and blocked counts.

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

When a split choice affects future reuse, editing, localization, animation, approximate reconstruction acceptance, candidate replacement, final delivery claims, or visual truth, ask the user one focused question before continuing. Include your recommended answer. Do not batch multiple questions unless the user asks for a full grill-me style interrogation.

Record each formal gate in `metadata.decision_log[]` and `metadata.confirmation`. If prior instructions or metadata already answer the question, record the evidence-backed decision instead of asking again. Progress commentary must not be stored as gate state.

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
