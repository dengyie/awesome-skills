# Asset Package Contract

This file defines the formal package contract surfaces. It is intentionally narrower than commentary, progress reporting, or casual review notes.

Use `quick-contract.md` when you need the short contract view. Use this file when you need the full package contract.

## Default Layout

```text
asset-package/
  source/
    source_original.png
  assets/
    main_object_transparent.png
    secondary_01_transparent.png
    secondary_group.png
    shadow_optional.png
    background_clean.png
  masks/
    mask_main.png
    mask_secondary_01.png
    mask_all_foreground.png
  previews/
    main_object_whitebg.png
    main_object_checkerboard.png
    main_object_mask_overlay.png
    main_object_alpha_inspection.png
    overview_decomposition.png
    sprite_sheet_2x2.png
  plan_manifest.json
  asset_manifest.json
  metadata.json
  qa_report.md
  _staging/
  _archive_intermediate/
```

Provider bridge request/result manifests should normally live under:

```text
_staging/providers/<provider-id>/<object-id>/request.json
_staging/providers/<provider-id>/<object-id>/result.json
```

Object counts vary. Prefer `main_object`, then `secondary_01`, `secondary_02`, and so on. Record the exact inventory in `metadata.json`. The underscored directories are for active external outputs and retained intermediate evidence; the formal package root should not contain ad hoc folders such as `external-sam-assets/` or temporary manifests.

## Metadata Fields

`metadata.json` must include:

- `schema_version`
- `package_name`
- `source.path`
- `source.width`
- `source.height`
- `analysis.visual_hierarchy`
- `analysis.recommended_split_plan`
- `granularity.mode`
- `granularity.user_confirmed`
- `granularity.notes`
- `granularity.scope_strategy`
- `granularity.text_handling`
- `granularity.carrier_glyph_policy`
- `granularity.background_expectation`
- `granularity.layer_independence`
- `capability.production_capable`
- `capability.missing_for_production`
- `capability.user_choice`
- `capability.notes`
- `quality_target.tier`
- `quality_target.notes`
- `confirmation`
- `decision_log`
- `extraction_pipeline.recipe`
- `extraction_pipeline.stages`
- `extraction_pipeline.quality_gates`
- `extraction_pipeline.tools`
- `audit`
- `objects`
- `asset_summary.production_ready_assets`
- `asset_summary.accepted_approximate_reconstructions`
- `asset_summary.accepted_generated_reconstructions`
- `asset_summary.draft_candidate_assets`
- `asset_summary.support_only_layers`
- `asset_summary.blocked_assets`
- `previews`
- `qa.status`

`analysis.visual_hierarchy` must name the semantic layer stack from background to foreground. `analysis.recommended_split_plan` must describe the reusable layer boundaries. Rectangular crop plans do not satisfy this field unless each rectangle is only a tight bbox around a semantic mask.

`plan_manifest.json` is a separate planning surface. It is not a duplicate of `metadata.json`. Use it to record whole-image planning, object route intent, attempt budgets, protected-object approval requirements, and generation-route reasoning before expensive extraction or generation begins.

The provider bridge layer is a separate execution-adapter surface. It is not a replacement for `metadata.json` or `plan_manifest.json`. Use it to standardize upstream provider requests and results before import, compare, promotion, or validation.
Provider bridge scripts must not mutate `metadata.json` directly. Requests and results stay in staging until an explicit consumer promotes them into package truth.

`granularity` records the agreed split scope for the run. Use values such as `module`, `component`, `atomic-layer`, `production-editable`, or `draft`. `user_confirmed` records whether the user explicitly aligned on that granularity, and `notes` captures any nuance such as live text rebuild or approximate background acceptance.

For UI or dense compositions, `granularity` must also record:

- `scope_strategy`: `high-signal-subset`, `full-image-batch`, or `unset`
- `text_handling`: `extract-as-image`, `rebuild-downstream`, or `unset`
- `carrier_glyph_policy`: `split`, `grouped`, `conditional`, or `unset`
- `background_expectation`: `exact-recovery`, `approximate-accepted`, or `unset`
- `layer_independence`: `static-reuse`, `animation-ready`, or `unset`

`capability` records the tooling preflight result before extraction. `production_capable` is the extraction-capable flag for non-generated reusable layers. `missing_for_production` lists missing upstream roles/tools such as `SAM2 or grounded detector` or `matting/refinement`. `user_choice` records `install-or-activate-tools`, `external-professional-outputs`, `draft-packaging-only`, `production-capable`, or `unset`. `notes` explains the quality implication of the choice.

`quality_target` records which target tier the run is aiming at:

- `structural-valid`
- `usable-draft`
- `visual-acceptance-ready`

`qa.status=pass` requires `quality_target.tier: visual-acceptance-ready`.

The preflight report should also expose:

- `missing_roles`
- `recommended_installs`
- `why_it_matters`

For reconstruction, runtime support such as `torch` or `onnxruntime` is not enough by itself to claim `production_ready`. Treat `manual_redraw_path` as a human acceptance path, not as automatic production capability.

`qa.status=pass` requires `capability.production_capable: true` whenever the package still claims non-generated reusable layers. Generated-only pass paths may keep `capability.production_capable: false`, but they must record `capability.generation.production_ready: true` and object-scoped generation-routing acceptance for every generated-route object. Draft-only or unrecorded tooling preflight must stay `needs-review` or `blocked`.

`decision_log` records confirmation-driven workflow decisions that materially affect reuse, editability, localization, reconstruction acceptance, or final delivery claims. Each entry must include:

- `stage`
- `pause_category`
- `question`
- `recommended_answer`
- `recorded_answer`
- `decision_effect`
- `decision_source`
- `evidence_ref`
- `blocking`

`decision_log` is a formal state surface and formal gate ledger, not a progress note stream.

- `pause_category` must be `user-decision`, `external-blocker`, or `formal-approval`
- `decision_source` may only be `explicit-user-confirmed` or `inferred-from-user`
- `agent-defaulted` is not legal in formal gate state
- `inferred-from-user` requires a non-empty `evidence_ref`
- `blocking` records whether this gate actually blocked downstream execution

If prior user instructions or existing metadata already answer the question, record that inferred decision instead of asking again. Do not leave subjective split choices only in chat.

`confirmation` records whether the hard workflow gates were actually cleared. It must include:

- `tooling_preflight`
- `granularity_alignment`
- `generation_routing`
- `pilot_object`
- `approximate_reconstruction`
- `final_acceptance`
- `candidate_promotion`

`final_promotion_acceptance` is a legacy alias for older packages only. New packages and current tooling must use `candidate_promotion` as the canonical promotion gate.

Each confirmation entry must include:

- `status`: `pending`, `confirmed`, or `not-required`
- `source`: `explicit-user-confirmed`, `inferred-from-user`, or `unset`
- `pause_category`
- `notes`
- `evidence_ref`

`pilot_object` must also include `object_id`.

`status=confirmed` or `status=not-required` may only use `explicit-user-confirmed` or `inferred-from-user`. `inferred-from-user` requires durable evidence and must not be used for agent guesswork.

`confirmation` is a formal state surface. It must not contain progress updates, routine commentary, or stage-complete summaries with no decision meaning.

Progress commentary, tool output summaries, and review notes must stay outside `decision_log` and `confirmation`. They can be stored in QA notes, but they do not count as formal gate evidence.

When a semantic divergence is object-specific, the confirmation evidence must stay object-scoped. Do not let one object's accepted split, approximation, or promotion decision implicitly satisfy another object's branch.

Each object should include:

- `id`
- `role`: `main`, `secondary`, `group`, `background`, or `shadow`
- `layer_kind`: `primary-subject`, `secondary-object`, `background`, `shadow`, `label`, `control`, `connection`, `frame`, `decoration`, or a similarly specific semantic category
- `composition_order`: integer layer stack order from background to foreground
- `semantic_boundary`
- `asset_path`
- `mask_path` when a mask exists
- `mask_source`
- `alpha_source`
- `bbox` when known
- `width`, `height`, `aspect_ratio`, and `area_ratio` when known
- `extraction_method`: `exact`, `ai-assisted`, `manual`, `estimated`, or `unknown`
- `confidence`: `high`, `medium`, or `low`
- `edge_complexity`: `hard`, `soft`, or `transparent-reflective`
- `object_type`: `ui-carrier`, `ui-glyph`, `carrier-glyph-pair`, `soft-edge-logo-brand-mark`, `outlined-illustration-logo`, `flat-support-plate`, `grouped-support-plate`, `photo-object-matte`, or `generic-object`
- `asset_class`: `atomic`, `grouped-support`, `background-support`, `preview-reference`, or `candidate`
- `reuse_status`: `production-ready`, `draft-candidate`, `support-only`, `blocked`, or `approximate-reconstruction`
- `delivery_class`: `clean-extraction`, `approximate-reconstruction`, `support-only`, or `draft-candidate`
- `current_asset_revision`
- `selected_candidate_id` when a staged candidate was promoted
- `repair_history[]` when the asset was retried or replaced
- `candidate_comparisons[]` when staged repair candidates were compared
- `active_reconstruction_method` when a layer is rebuilt or approximated
- `value_scoring.editability_score`
- `value_scoring.visual_complexity_score`
- `value_scoring.asset_value_score`
- `value_scoring.scoring_reason`
- `decision_routing.recommended_action`
- `decision_routing.final_action`
- `decision_routing.decision_source`
- `rebuild_intent.rebuildable_downstream`
- `rebuild_intent.rebuild_notes`
- `text_semantics.text_role`
- `text_semantics.text_render_class`
- `quality_checks.mask_alignment`
- `quality_checks.alpha_edges`
- `quality_checks.background_residue`
- `quality_checks.reuse_readiness`
- `manual_review_flags`
- `manual_review_confirmed` when a crop-only or estimated layer is manually approved for production reuse
- `approximate` and `reconstruction_provenance` when a layer was reconstructed, inpainted, or approximated rather than extracted exactly

Planning-time route data belongs primarily in `plan_manifest.json`, not in long-lived object state inside `metadata.json`. During rollout, `plan_manifest` uses the planning routes:

- `extract`
- `reconstruct`
- `generate`
- `rebuild_downstream`
- `support_only`

Current execution-state routing in `metadata.json` still uses:

- `extract_asset`
- `rebuild_downstream`
- `requires_user_confirmation`
- `support_only`

Do not silently overwrite `decision_routing.final_action` with raw planning route strings.

Use `asset_summary` to keep final counts honest. Production asset counts should only include `asset_class: atomic` plus `reuse_status: production-ready`. Draft-only runs should normally report `production_ready_assets: 0` even when many candidate PNGs exist.

The routing metadata should follow these allowed values:

- `text_semantics.text_role`: `plain-text`, `button-label`, `numeric-value`, `form-value`, `logo-wordmark`, `decorative-text`, or `non-text`
- `text_semantics.text_render_class`: `editable`, `styled-editable`, `visual-fidelity-critical`, or `non-text`
- `value_scoring.*_score`: `unset`, `low`, `medium`, or `high`
- `decision_routing.recommended_action` / `decision_routing.final_action`: `extract_asset`, `rebuild_downstream`, `requires_user_confirmation`, `support_only`, or `unset`

Use `rebuild_downstream` for ordinary editable text-like content. Use `extract_asset` for visually fidelity-critical text such as logo wordmarks or decorative text. Use `requires_user_confirmation` for ambiguous high-complexity text-like objects that cannot be safely auto-routed.

For UI-like assets, `object_type` must not stay `generic-object`. The workflow should make routing visible to future agents and reviewers.

## Plan Manifest Contract

`plan_manifest.json` is the planning-time route truth surface. It should exist before formal extraction or generation work begins, even if it initially contains only a partial inventory.

At minimum, `plan_manifest.json` should include:

- `schema_version`
- `package_name`
- `source.path`
- `source.width`
- `source.height`
- `quality_target.tier`
- `planning_status.status`
- `route_policy.planning_required`
- `route_policy.generation_routing_gate`
- `provider_preferences.generation_provider_class`
- `objects`
- `summary`

Each planned object entry should be able to record:

- `object_id`
- `object_type`
- `planned_route`
- `route_signals.recoverability_low`
- `route_signals.object_is_reconstruction_like`
- `route_signals.quality_target_high`
- `route_signals.segmentation_cost_unfavorable`
- `route_score`
- `route_reason`
- `needs_user_confirmation`
- `attempt_budget`
- `attempts_used`
- `attempt_history`
- `token_budget_hint`
- `pilot_group`
- `promotion_requirement`
- `protected_policy`
- `protected_approval_required`
- `protected_approval_ref`

For planned `generate` objects, also record:

- `why_not_extract`
- `why_not_reconstruct`
- `why_generate`
- `risk_note`

During rollout, validator enforcement for missing `plan_manifest` should be staged:

1. the file may exist without global hard enforcement
2. generated-route objects become the first hard-enforced path
3. broader enforcement may expand only after fixtures and helpers are migrated

## Generation Capability Contract

Tooling preflight should report generation capability separately from segmentation capability.

Generation capability should use:

- `installed`
- `runtime_ready`
- `production_ready`

Recognized provider classes should include:

- `codex-controlled-generation`
- `external-generated-outputs`
- `local-model-runtime`

Generation capability is not `production_ready` unless the provider can support:

- object-level reference-constrained generation
- transparent object-asset delivery
- durable evidence suitable for compare, promotion, and reporting

Missing segmentation tooling alone must not be used as the reason to claim a generated delivery path.

## Provider Bridge Contract

Provider request/result manifests should use package-relative paths only and should stay inside `_staging/providers/` while active.

Provider requests should capture:

- provider identity
- provider role
- execution mode
- object identity
- planned route
- quality target
- source and input refs
- expected outputs

Provider results should capture:

- provider identity
- result status
- package-relative artifacts
- structured provenance
- warnings
- whether the provider believes the result is production-ready
- the next expected provider when the chain continues

## Generated-Reconstruction Contract

`generated-reconstruction` is a distinct delivery truth class from both clean extraction and approximate reconstruction.

During rollout, it should be introduced as a coordinated contract migration across shared constants, review writing, validation, summary counting, and downstream manifest export.

Generated-route evidence should eventually include:

- `generation_source`
- `model_or_tool`
- `version`
- `prompt_or_brief_ref`
- `reference_inputs`
- `candidate_id`
- `compare_evidence`
- `promotion_acceptance`
- `selection_reason`

## Pipeline Contract

`extraction_pipeline` records how the package was produced. Use `grounded-segmentation-matting-repair` for a Grounded-SAM/SAM2 style mask pipeline followed by matting and background repair. Use `layered-rgba-decomposition` for Qwen-Image-Layered style multi-layer proposals.

The ordered `stages` list must include `semantic-analysis`, `segmentation`, `alpha-refinement`, `layer-packaging`, and `qa-review`. Add `detection`, `background-repair`, `layered-decomposition`, or `recursive-layer-review` when those stages are used.

`quality_gates` should name the checks performed before final status. `tools` must record external models, services, manual editing, or user-provided assets as objects with `name`, `role`, and `version` when known. Use `"unknown"` for a version only when the tool version cannot be recovered.

`qa.status` can be `pass`, `needs-review`, or `blocked`. Do not use `pass` when any required object `quality_checks` value is `needs-review`, `blocked`, or `unknown`.

Do not use `reuse_status: production-ready` when `capability.production_capable` is false or `capability.user_choice` is `draft-packaging-only`. Draft-only imported results should remain `candidate` plus `draft-candidate`, and support plates should remain `support-only`.

## Production Assets Versus Previews

Transparent object PNGs, masks, and cleaned backgrounds are production assets.

Only inspected atomic transparent object PNGs with `reuse_status: production-ready` should be counted as production reusable assets. Support plates, grouped UI chrome, preview references, and approximate backgrounds may be useful package files but should be counted separately.

White-background previews, checkerboard previews, overview layouts, and 2x2 sprite sheets are inspection artifacts. They help review the package but do not replace the reusable assets.

Mask overlays and alpha inspection previews generated by `build_quality_previews.py` are QA evidence. They should be referenced from `metadata.previews.quality` and inspected before any `pass` status.

Validation requires preview evidence. For every reusable object layer, `metadata.previews` must reference white-background and checkerboard inspection previews, and `metadata.previews.quality` must reference mask overlay and alpha inspection previews. Packages with object layers but missing preview evidence are structurally incomplete even if their PNG assets and masks exist.

`assets/*.png` are tight transparent reusable layers. `masks/*.png` are normally source-space QA masks with the same dimensions as `source/source_original.png`. This means a small UI glyph may have a mostly black mask with a small white region; that is expected and helps overlay inspection and provenance tracing.

## Downstream Asset Manifest

`asset_manifest.json` is a consumer-facing index generated by `scripts/export_asset_manifest.py`. It contains package name, source dimensions, QA status, extraction recipe, and reusable layers sorted by `composition_order`.

Use it for renderer integration, animation handoff, design-tool import, or manual review queues. Do not edit it as the source of truth; regenerate it from `metadata.json` after package changes.

## Semantic Assets Versus Crops

An object's `bbox` records storage bounds. It is not the object's identity. A valid asset is tied to a semantic layer such as a background, object, label group, route network, shadow, frame, or decoration.

If an asset exists only because it is a convenient rectangular crop, mark it as a preview or replace it with a semantic mask-backed asset before validation.

If a layer uses `mask_source` such as `bbox`, `crop`, or `manual-estimated crop`, it is crop-only draft evidence by default. A package-level `qa.status=pass` is invalid until the object records `manual_review_confirmed: true` through an explicit manual review step.

If a layer represents an approximate clean plate, support plate, or reconstructed UI structure, record `approximate: true` and `reconstruction_provenance`. It must remain `needs-review` unless a human explicitly confirms the layer as acceptable.

Approximate or reconstructed layers must not use `reuse_status: production-ready`. Use `delivery_class=approximate-reconstruction` and keep them separate from clean extraction counts.

`audit.quality_audit_path` must point into `_staging/` or `_archive_intermediate/`, never the package root. Use it for warning-only quality audit evidence, not final deliverables.

For UI icon-in-tile, badge-in-card, or glyph-on-plate structures, prefer separate semantic layers such as `status_row_02_icon_tile` and `status_row_02_icon_glyph` when downstream reuse or edge cleanup benefits from that separation.

Carrier/glyph splits should each have their own source-space mask overlay. If a glyph still contains carrier or background color, keep `reuse_status: draft-candidate` or set `quality_checks.background_residue: blocked`.

Structural validation does not prove visual perfection. It proves the package has enough pipeline and quality evidence for a human or downstream agent to inspect segmentation quality.

## External Tool Import Contract

Use `scripts/import_external_assets.py` when importing outputs from SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual editing, or user-provided files. The importer copies files into package-controlled `assets/` and `masks/` paths and records upstream tool provenance in `metadata.extraction_pipeline.tools`.

Imported layers default to `needs-review` quality checks because external generation is not the same as inspected production readiness.

Imported layers should also default to `asset_class: candidate` and `reuse_status: draft-candidate`. Promote them only after preview inspection, warning audit review, and user/manual acceptance when subjective boundaries are involved.

The importer expects masks to be source-space masks. If an upstream tool only produced a tight bbox mask, expand it back into source coordinates before importing or keep it in `_staging/` as an intermediate.

## Manual Review Recording Contract

Use `scripts/record_quality_review.py` after preview inspection to avoid hand-editing drift between `metadata.json` and `qa_report.md`.

The script can record:

- `analysis.visual_hierarchy`
- `analysis.recommended_split_plan`
- `granularity.mode`
- `granularity.user_confirmed`
- `granularity.notes`
- `capability.production_capable`
- `capability.missing_for_production`
- `capability.user_choice`
- `capability.notes`
- `decision_log` confirmation entries
- object `asset_class`
- object `reuse_status`
- `extraction_pipeline.quality_gates`
- object-level `quality_checks`
- package `qa.status`
- review notes in `qa_report.md`

The script rejects `qa.status=pass` unless every required object quality check is already `pass` or is updated to `pass` in the same command.

It also rejects `qa.status=pass` unless reusable layers have been promoted to `reuse_status: production-ready`.

## Intermediate Archive Contract

Use `scripts/archive_intermediates.py` when moving retained `_staging/` outputs into `_archive_intermediate/<run-id>/`. The helper writes `archive_manifest.json` so future reviewers can see which upstream candidate masks, temporary manifests, or refinement outputs were retained.

Use `scripts/compare_candidate_assets.py` when more than one repair candidate should be reviewed. `candidate_comparisons[]` should record:

- `comparison_id`
- `candidate_ids`
- `compare_artifact_path`
- `compare_manifest_path`
- `compare_note`
- `compare_criteria`
- `review_focus`
- `risks`
- `score_manifest_path` when `score_candidate_assets.py` was used
- `selected_candidate_id`
- `selection_reason`

Multi-candidate promotions should not happen without compare evidence. Compare manifest files are hard evidence, not optional sidecars.
