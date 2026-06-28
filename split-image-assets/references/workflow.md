# Split Image Assets Workflow

## Purpose

Use this runbook to decide when the split-image-assets workflow keeps moving and when it is allowed to stop for a human.

Default rule: continue in `Running` unless the next branch is a real `AwaitingDecision`, `AwaitingExternalBlocker`, or `AwaitingApproval` event. Progress-only pauses are not allowed.

## State Taxonomy

- `Running`: normal execution, evidence capture, packaging, previews, audits, validation
- `AwaitingDecision`: a user choice is required because different answers change package semantics
- `AwaitingExternalBlocker`: execution cannot continue without tools, outputs, installs, credentials, or another external prerequisite
- `AwaitingApproval`: the package has enough evidence to request a formal approval gate
- `Completed`: the current run has reached a terminal outcome

## Allowed Stop Classes

- `user-decision` -> `AwaitingDecision`
- `external-blocker` -> `AwaitingExternalBlocker`
- `formal-approval` -> `AwaitingApproval`

The stop class says why the workflow is allowed to stop. The state says which waiting state the run enters after that stop.

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

When a stage is in `Running`, keep going and report commentary only.

Stopping is allowed only when all of the following are true:

1. The stop maps to one of `AwaitingDecision`, `AwaitingExternalBlocker`, or `AwaitingApproval`.
2. The minimum evidence for that stop has been gathered.
3. Prior user instructions and recorded metadata do not already answer the question.

If pause is not allowed, continue with the documented fallback and record the rationale in metadata instead of stopping.

## Gate Runbook

### `tooling_preflight`

- Formal gate name: Preflight Tooling Recommendation Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed stop class: `external-blocker`
- Stop state: `AwaitingExternalBlocker`
- Minimum evidence before stop:
  - `scripts/check_extraction_environment.py` report captured
  - missing roles identified for detection, segmentation, alpha refinement/matting, or reconstruction
  - `production_capable`, `missing_for_production`, `missing_roles`, `recommended_installs`, and `why_it_matters` available
- Stop only when:
  - the workflow cannot honestly claim a production-capable path without a user choice or external outputs
- Continue behavior when pause is not allowed:
  - if prior instructions already select `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`, record that in `metadata.capability`, `metadata.confirmation.tooling_preflight`, and `metadata.decision_log[]`, then continue
  - if the environment is already production-capable, record the evidence and continue without stopping

### `granularity_alignment`

- Formal gate name: Granularity Alignment Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed stop class: `user-decision`
- Stop state: `AwaitingDecision`
- Minimum evidence before stop:
  - semantic layer hierarchy analyzed
  - candidate split choices identified for granularity, text handling, carrier/glyph policy, background expectation, and layer independence
  - at least one branch would materially change reuse boundaries or downstream rebuild expectations
- Stop only when:
  - existing instructions and metadata do not already settle those branches
- Continue behavior when pause is not allowed:
  - if user intent is already durable, record `mode`, `scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, `layer_independence`, `metadata.confirmation.granularity_alignment`, and a decision-log entry, then continue
  - if the image is straightforward and the split is clearly derivable, continue with the recorded rationale instead of asking again
  - ordinary editable text-like objects should continue on the `rebuild_downstream` path unless the recorded policy or later evidence explicitly upgrades them to visual assets

### `pilot_object`

- Formal gate name: Pilot Object Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed stop class: `formal-approval`
- Stop state: `AwaitingApproval`
- Minimum evidence before stop:
  - image class is dense UI, dashboard, badge/tile/glyph, or another high-risk composition
  - one representative object has been selected as the pilot
  - the pilot’s granularity and cleanliness can be demonstrated with package evidence
- Stop only when:
  - widening extraction without pilot signoff would materially increase cleanup cost or semantic drift
- Continue behavior when pause is not allowed:
  - if prior user instruction or recorded policy makes the pilot `not-required`, record that in `metadata.confirmation.pilot_object` and continue with the broader batch
  - if the composition is simple, document why no pilot stop is needed and continue

### `approximate_reconstruction`

- Formal gate name: Approximate Reconstruction Acceptance Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed stop class: `user-decision`
- Stop state: `AwaitingDecision`
- Minimum evidence before stop:
  - exact hidden pixels are unavailable
  - the layer would rely on inferred pixels, inpainting, manual redraw, or another approximate path
  - the package can describe the affected asset and the reconstruction provenance
- Stop only when:
  - approximate delivery would change truthfulness, quality claims, or downstream use
- Continue behavior when pause is not allowed:
  - if prior instructions already allow approximation, keep the asset classified as approximate, record `delivery_class=approximate-reconstruction`, `reconstruction_provenance`, `active_reconstruction_method`, `metadata.confirmation.approximate_reconstruction`, and continue
  - if approximation is not accepted, keep the layer `needs-review` or `blocked` and continue with the draft-honest path instead of stopping for a progress update

When a split choice affects future reuse, editing, localization, animation, approximate reconstruction acceptance, candidate replacement, final delivery claims, or visual truth, ask the user one focused question before continuing. Include your recommended answer. Do not batch multiple questions unless the user asks for a full grill-me style interrogation.

Record each formal gate in `metadata.decision_log[]` and `metadata.confirmation`. If prior instructions or metadata already answer the question, record the evidence-backed decision instead of asking again. Progress commentary must not be stored as gate state.

### `candidate_promotion`

- Formal gate name: Candidate Promotion Acceptance Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed stop class: `formal-approval`
- Stop state: `AwaitingApproval`
- Minimum evidence before stop:
  - a candidate asset is ready to replace the current revision
  - compare evidence or a direct-promotion rationale exists
  - the selected candidate and revision impact are known
- Stop only when:
  - replacing the current revision requires formal approval and no prior approved promotion rule already covers it
- Continue behavior when pause is not allowed:
  - if an existing accepted policy already authorizes the promotion, record `metadata.confirmation.candidate_promotion`, `selected_candidate_id`, `current_asset_revision`, `repair_history[]`, `candidate_comparisons[]`, and continue
  - if approval is absent, keep the candidate staged and continue with review evidence capture rather than promoting silently

## Standard Execution Path

1. Inspect or initialize the package.
2. Run `tooling_preflight`.
3. Select recipe and analyze semantic layers.
4. Run `granularity_alignment`.
5. Use a `pilot_object` when the composition is dense or high-risk.
6. Extract or import assets and masks.
7. If needed, resolve `approximate_reconstruction`.
8. Build previews, quality previews, audits, and QA evidence.
9. Validate structure and export the manifest.
10. Request `final_acceptance` and `candidate_promotion` only when the evidence actually supports those approval gates.

## Stop Hygiene

- Do not stop for progress-only pauses.
- Do not stop because a stage finished.
- Do not ask multiple unrelated questions in one stop.
- Do not ask for a decision that prior instructions already resolved.
- Do not convert commentary into a fake gate just to summarize work.
