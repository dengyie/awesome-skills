# Split Image Assets

Use `split-image-assets` when a source image needs to become a reusable asset package instead of a single preview image.

The skill helps produce transparent PNG object layers, mask files, `background_clean.png`, `metadata.json`, `qa_report.md`, and inspection previews such as `sprite_sheet_2x2.png`.

Use it when the main job is packaging reusable visual assets with honest QA and metadata, not when you only need a quick crop or a fully automatic segmenter.

The deterministic script layer does not perform segmentation. Use AI image editing, segmentation tools, manual editing, or user-provided cutouts to create object assets, then use the scripts to initialize, preview, and validate the package.

## What it produces

Typical outputs:

- transparent PNG layers
- source-space masks
- `background_clean.png`
- `metadata.json`
- `qa_report.md`
- reusable preview evidence

If you are still choosing among skills, go back to the [Skill Matrix](skill-matrix.md). If you only need installation help, use the [Quickstart](quickstart.md).

## Related docs

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [Examples](examples.md)
- [Troubleshooting](troubleshooting.md)

## Read What Where

Use this page as the operator guide.

For deeper details, use the more specialized sources instead of treating this file as the full contract:

- `docs/superpowers/split-image-assets/design.md`: architecture intent and rollout strategy
- `docs/superpowers/split-image-assets/implementation-plan.md`: current shipped baseline and next bounded milestone candidates
- `split-image-assets/SKILL.md`: agent-facing workflow entrypoint
- `split-image-assets/references/workflow.md`: gate and state-machine detail
- `split-image-assets/references/asset-package-contract.md`: package contract and validator truth surface
- `split-image-assets/references/provider-contract.md`: provider bridge request/result contract
- `split-image-assets/references/default-route-chains.md`: default provider chains per route
- `split-image-assets/references/pipeline-recipes.md`: route and recipe choice
- `split-image-assets/references/ui-atomic-split.md`: UI-specific planning

The default production path is professional upstream -> import -> preview -> QA review -> validate -> manifest. This skill is the workflow, packaging, and QA tail of that chain; it is not the upstream segmenter.

The workflow is now planning-first. Before expensive extraction or generation work begins, create and maintain `plan_manifest.json` so the package can record whole-image planning, object routes, attempt budgets, protected-object restrictions, and generated-route reasoning separately from final package state.

Before extraction, always declare the quality target tier:

- `structural-valid`
- `usable-draft`
- `visual-acceptance-ready`

For quality-first extraction, use a Grounded-SAM/SAM2 style pipeline: semantic analysis, text-guided detection, segmentation, alpha refinement with rembg/BiRefNet/RMBG-style tools, background repair with inpainting or manual paint work, then QA. For layer-first decomposition, use Qwen-Image-Layered style RGBA layer proposals, then inspect every layer before treating it as production-ready.

Start by recording a semantic layer hierarchy in `metadata.analysis.visual_hierarchy`. Split by meaning: background/backplate, frame or UI chrome, main subjects, connection paths, labels, buttons, decorations, shadows, and overlays. A rectangular crop is only acceptable as a tight storage bbox around a semantic mask; rectangular crop packages are not complete asset packages.

## Default Execution Model

The default execution model is conservative continuous execution. Keep running by default, and stop only when one of the three formal stop classes is justified by the next branch.

Progress updates are commentary, not confirmation gates. Reporting that validation is running, previews are building, or QA evidence is being collected should not pause the workflow.

### Continue Versus Stop

| Situation | Continue | Stop |
| --- | --- | --- |
| Normal progress | analysis, import, preview generation, QA inspection, validation, and metadata updates stay in `Running` | do not stop just to report progress |
| Hard stop event | keep going only if existing evidence already resolves it | stop for a real user decision, external blocker, or formal approval |
| Semantic divergence | continue when the next step preserves the already-agreed package semantics | stop only by using a real `user-decision` event when medium/high-risk semantic divergence would change reuse boundaries, text ownership, background acceptance, or production claims |

Anti-example: “I finished preview generation and validation is next. Should I continue?” This is a progress-only pause and should not happen.

Positive example: “The logo text could be exported as a raster asset or rebuilt downstream. This is medium-risk semantic divergence because it changes reuse semantics. Recommendation: rebuild downstream unless exact brand styling must stay baked into pixels. After confirmation, I will either record `rebuild_downstream` and continue QA or preserve the wordmark as an extracted asset and continue packaging.”

## Before extraction

Run the Preflight Tooling Recommendation Gate before starting a high-quality split:

```bash
python split-image-assets/scripts/check_extraction_environment.py
```

If mature segmentation/matting tools are unavailable and no external masks or cutouts were provided, do not claim production extraction. Explain which upstream role is missing, what quality it affects, and ask whether to install or activate tools, provide external professional split outputs, or continue as draft-packaging-only.

For reconstruction, do not treat `torch` or `onnxruntime` as enough to claim a production reconstruction path. Without a dedicated reconstruction tool, the honest fallback is `manual redraw required` or `approximate reconstruction only`.

Generation capability should be reported separately from segmentation capability. It should distinguish `installed`, `runtime_ready`, and `production_ready`, and it is not `production_ready` unless the provider can support object-level constrained generation plus transparent object-asset delivery.

The preflight report should explicitly call out:

- `missing_roles`
- `recommended_installs`
- `why_it_matters`

Always report whether the run is `production-capable` or `draft-packaging-only`. If it is not production-capable, explicitly list what is missing, record the user choice in `metadata.capability`, and keep the package honest.

Missing upstream role examples:

- missing SAM2 or grounded detector: object boundaries may need manual prompts or may be less reliable
- missing rembg/BiRefNet/RMBG: alpha edges may keep halos, dark fringes, or background residue
- missing inpainting/manual repair path: `background_clean.png` can only be approximate or `needs-review`

Also align split granularity before cutting pixels: module-level, component-level, atomic-layer, or production-editable reconstruction; text as image assets or live downstream text; exact background recovery or approximate `background_clean.png`; animation-ready layers or static reuse.

Run asset value scoring before extraction. Use an editability-first default: ordinary text, button labels, numeric values, and form values should normally stay out of raster export and route to `rebuild_downstream`. Logo wordmarks, decorative text, and other visual-fidelity-critical text may still route to `extract_asset`. When a text-like object is visually complex and ambiguous, route it to `requires_user_confirmation` instead of silently extracting it.

Then run object-route planning in `plan_manifest.json`. Use the planning routes:

- `extract`
- `reconstruct`
- `generate`
- `rebuild_downstream`
- `support_only`

For generated-route planning, evaluate the four lightweight route signals:

- `recoverability_low`
- `object_is_reconstruction_like`
- `quality_target_high`
- `segmentation_cost_unfavorable`

Default threshold policy:

- `3/4`: recommend `generate`
- `2/4`: stop for `Generation Routing Gate`
- `0-1/4`: continue on the non-generation path

Do not route to `generate` merely because local segmentation tooling is missing.

After route planning, choose the default provider chain for that route, then apply any explicit `object_type` override; this is the route default plus object_type override rule for provider selection. Run `describe_provider_plan.py` before broad request generation so `_staging/providers/provider_plan.json` makes the selected provider, selection source, and alternative providers explicit. Then run `describe_provider_work_items.py` so `_staging/providers/provider_work_items.json` tells you whether each object should prepare a generation brief, prepare a provider request, wait for an upstream result, or consume a staged result. `prepare_provider_request.py` should be able to use that rule without forcing `--provider-id` every time. Write provider bridge request manifests into `_staging/providers/<provider-id>/<object-id>/`. V1 intentionally keeps the active provider surface narrow to `external-professional-outputs`, `external-generated-outputs`, `codex-controlled-generation`, and `grounded-sam-bridge`. The bridge layer comes before broad native-runner expansion: it standardizes what the skill asks of upstream providers and what they must return, and its request/result scripts must not write `metadata.json` directly.

Also classify each target object before choosing the repair path:

- `ui-carrier`
- `ui-glyph`
- `carrier-glyph-pair`
- `soft-edge-logo-brand-mark`
- `outlined-illustration-logo`
- `flat-support-plate`
- `photo-object-matte`

When granularity, carrier/glyph grouping, text ownership, approximate background acceptance, low-confidence masks, or final `pass` claims are subjective, use a grill-me style confirmation step: ask one focused question, include your recommended answer, resolve that branch, then record the outcome in `metadata.decision_log[]`. If prior instructions already answer the question, record the decision instead of asking again.

progress updates are commentary, not confirmation gates. Only three event classes should pause execution: real user decisions, genuine external blockers, and formal approval points.

Treat these as formal gates:

- `Preflight Tooling Recommendation Gate`
- `Granularity Alignment Gate`
- `Generation Routing Gate`
- `Pilot Object Gate`
- `Approximate Reconstruction Acceptance Gate`
- `Final Acceptance Gate`
- `Candidate Promotion Acceptance Gate`

Carrier/glyph disagreement is not a separate formal gate anymore. It is a decision branch inside `Granularity Alignment Gate`, and should reuse that gate's state, recommendation pattern, and metadata surface.

Each gate should ask one decisive question, offer a recommended answer, and update metadata in a durable way rather than leaving the choice only in chat.

### Allowed Stop Examples

True external blocker stop: “Production-capable extraction is blocked because the environment still lacks segmentation and matting outputs. Recommendation: use `external-professional-outputs` unless you want to pause for tool installation. After confirmation, I will record the preflight decision in `metadata.capability` and continue on the selected path.”

Correct semantic divergence stop: “This dashboard badge can stay grouped, or the carrier and glyph can split into separate reusable layers. This is medium-risk semantic divergence because it changes reuse boundaries. Recommendation: split the carrier and glyph. After confirmation, I will record the decision in `metadata.decision_log[]` and continue extraction without reopening the branch.”

Correct formal approval stop: “The pilot object now has previews, quality overlays, and QA notes. This is a formal approval point because widening the batch would reuse this cleanliness standard. Recommendation: approve the pilot if this granularity is acceptable. After confirmation, I will either continue the broader batch or keep work on the pilot.”

Progress-only anti-example: “Preview generation is done and validation is next.” This should remain commentary, not a stop.

Use a professional segmenter or matting pipeline as the primary source for production masks. Pillow, OpenCV, and skimage are helpers for alpha compositing, source-space mask persistence, preview generation, repair, and packaging; they are not a substitute for SAM2/SAM/Grounded-SAM/rembg/BiRefNet/RMBG-style extraction.

For complex UI screenshots, start with a high-signal subset such as logo, nav icon, status dot, pin, checkbox, chart mark, badge, or row glyph. For icon-in-tile or glyph-on-plate elements, split the tile/badge/panel background from the foreground glyph when reuse or edge cleanup benefits from separate layers.

For UI repair workflows, prefer the dedicated helper scripts:

- `generate_ui_carrier_candidates.py`
- `generate_ui_glyph_cleanup_candidates.py`
- `score_candidate_assets.py`
- `upscale_repair_downscale.py`

## Output Package

```text
asset-package/
  source/source_original.png
  assets/main_object_transparent.png
  assets/background_clean.png
  masks/mask_main.png
  previews/sprite_sheet_2x2.png
  plan_manifest.json
  asset_manifest.json
  metadata.json
  qa_report.md
  _staging/
  _archive_intermediate/
```

`metadata.json` must also include `analysis.visual_hierarchy`, `analysis.recommended_split_plan`, `extraction_pipeline`, and per-object quality evidence so reviewers can tell whether extraction followed the image structure instead of only cutting page regions.
It should also record `granularity.mode`, `granularity.user_confirmed`, `granularity.notes`, `capability.production_capable`, `capability.missing_for_production`, `capability.user_choice`, `capability.notes`, and `decision_log[]` so later agents can see what split scope, tooling capability, and subjective decisions were agreed.
Formal gate metadata should use `recorded_answer`, `pause_category`, `decision_source`, `evidence_ref`, and `blocking`. `inferred-from-user` is only valid when that evidence can be cited, and `agent-defaulted` must not satisfy a formal gate.
It should also record `quality_target.tier`, `quality_target.notes`, and per-object `object_type` so later agents can see whether the package is only structurally valid, a usable draft, or ready for visual acceptance.
For asset value routing, also record per-object `value_scoring`, `decision_routing`, `rebuild_intent`, and `text_semantics`. This keeps text-like objects auditable when they are rebuilt downstream instead of exported as image assets.

`plan_manifest.json` is the planning-time route surface. Use it for `planned_route`, route signals, attempt budgets, protected-object approval requirements, and generated-route reasoning. Keep final package state in `metadata.json`; do not collapse the two files into one vague surface.

`assets/*.png` are reusable transparent layers. `masks/*.png` are source-space QA masks aligned to the original image, so a small object may appear as a small white region on a mostly black mask. Put active external model outputs, candidate masks, and temporary manifests in `_staging/`; move retained evidence to `_archive_intermediate/` before final validation.

## Basic Commands

```bash
python split-image-assets/scripts/check_extraction_environment.py
python split-image-assets/scripts/init_asset_package.py source.png output-package
python split-image-assets/scripts/prepare_generation_brief.py output-package --object-id main_object --reference-input source/source_original.png
python split-image-assets/scripts/describe_provider_plan.py output-package
python split-image-assets/scripts/describe_provider_work_items.py output-package
python split-image-assets/scripts/prepare_provider_request.py output-package --object-id main_object --input-ref source_crop=_staging/planning/main_object_crop.png --input-ref rough_mask=_staging/planning/main_object_mask.png
python split-image-assets/scripts/record_provider_result.py output-package --provider-id grounded-sam-bridge --object-id main_object --status success --artifact asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png --artifact source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png --tool-name Grounded-SAM --tool-role segmentation --tool-version external --execution-mode bridge --next-expected-provider rembg-bridge
python split-image-assets/scripts/consume_provider_result.py output-package --provider-id grounded-sam-bridge --object-id main_object --mode import-extract --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject imported from provider result"
python split-image-assets/scripts/consume_provider_result.py output-package --provider-id external-professional-outputs --object-id main_object --mode import-manifest
python split-image-assets/scripts/consume_provider_result.py output-package --object-id main_object
python split-image-assets/scripts/consume_provider_result.py output-package --provider-id codex-controlled-generation --object-id main_object --mode stage-candidate --candidate-id generated-v1
python split-image-assets/scripts/promote_candidate_asset.py output-package --object-id main_object --candidate-id generated-v1 --comparison-id main_object-compare-20260704113000 --delivery-class generated-reconstruction --repair-note "Promote selected generated candidate." --selection-reason "Selected candidate best matches the approved generated compare."
python split-image-assets/scripts/import_external_assets.py output-package --object-id main_object --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject from SAM2 mask" --asset main.png --mask mask_main.png --mask-source sam2 --alpha-source rembg --tool-name SAM2 --tool-role segmentation --tool-version external
python split-image-assets/scripts/build_previews.py output-package
python split-image-assets/scripts/build_quality_previews.py output-package
python split-image-assets/scripts/audit_visual_quality.py output-package
python split-image-assets/scripts/generate_ui_carrier_candidates.py output-package --object-id status_row_02_icon_tile --source-crop _staging/tile_source.png --carrier-mask masks/mask_status_row_02_icon_tile.png --glyph-mask masks/mask_status_row_02_icon_glyph.png
python split-image-assets/scripts/generate_ui_glyph_cleanup_candidates.py output-package --object-id status_row_02_icon_glyph --glyph-asset assets/status_row_02_icon_glyph_transparent.png --carrier-reference assets/status_row_02_icon_tile_transparent.png
python split-image-assets/scripts/score_candidate_assets.py output-package --object-id status_row_02_icon_tile --candidate candidate-a=_staging/repair_candidates/status_row_02_icon_tile/candidate_a.png --candidate candidate-b=_staging/repair_candidates/status_row_02_icon_tile/candidate_b.png --reference-asset assets/status_row_02_icon_tile_transparent.png
python split-image-assets/scripts/describe_candidate_work_items.py output-package
python split-image-assets/scripts/record_candidate_promotion_approval.py output-package --object-id main_object --comparison-id cmp-1 --decision-answer yes --evidence-ref chat:promotion-approved
python split-image-assets/scripts/upscale_repair_downscale.py output-package --object-id status_row_02_icon_glyph --source-asset assets/status_row_02_icon_glyph_transparent.png --source-mask masks/mask_status_row_02_icon_glyph.png --scale 2
python split-image-assets/scripts/record_quality_review.py output-package --production-capable true --capability-user-choice production-capable --capability-note "SAM2 and rembg-style external outputs were provided." --visual-hierarchy background --visual-hierarchy "main object" --recommended-split-plan "Keep the main object separate from the background." --granularity-mode atomic-layer --granularity-confirmed --granularity-note "Atomic foreground layers; text rebuilt downstream." --decision-stage tooling-preflight --decision-question "Install tools, provide external outputs, or continue draft-only?" --decision-recommended "Install/provide SAM2 or Grounded-SAM plus rembg/BiRefNet/RMBG for production-quality extraction." --decision-answer "external professional outputs provided" --decision-effect "Use imported professional outputs and allow pass only after QA evidence passes." --quality-gate "mask overlay inspected" --object-id main_object --asset-class atomic --reuse-status production-ready --mask-alignment pass --alpha-edges pass --background-residue pass --reuse-readiness pass --qa-status pass --review-note "Manual inspection accepted the imported layer."
python split-image-assets/scripts/archive_intermediates.py output-package --run-id sam-pass-001
python split-image-assets/scripts/validate_asset_package.py output-package
python split-image-assets/scripts/export_asset_manifest.py output-package
```

`asset_manifest.json` is the downstream handoff file for renderers, animation tooling, design imports, or manual review queues. It is generated from `metadata.json`, sorted by `composition_order`, and uses package-relative paths.

Each object should declare `asset_class` and `reuse_status`. Use `atomic` + `production-ready` only after review promotion, `candidate` + `draft-candidate` for imported or unreviewed cutouts, and support classes/statuses for grouped plates, background clean plates, preview references, and UI chrome. Draft-only packages must report `not production reusable`.

Generated delivery is a distinct truth class. Use `generated-reconstruction` only when the package also carries route reasoning, provider/tool identity, brief reference, compare evidence, promotion approval, and selection rationale.

Final summaries should separate:

- production-ready assets
- accepted approximate reconstructions
- accepted generated reconstructions
- draft candidate assets
- support-only layers
- blocked assets

Large plates, approximate `background_clean`, screenshot-level support layers, and grouped UI chrome should not be counted as atomic production-ready assets.

## QA

Use `pass` only when reusable assets, masks, metadata, previews, and background repair are acceptable. Use `needs-review` when edge quality, AI-assisted regions, object roles, or background repair need manual review. Use `blocked` when required files are missing or the package cannot be reused safely.

`qa.status=pass` requires extraction-capable `metadata.capability.production_capable=true` whenever the package still claims non-generated reusable layers. Generated-only pass paths instead require `metadata.capability.generation.production_ready=true` plus object-scoped generation-routing evidence. Keep draft-only or unrecorded tooling-preflight packages `needs-review` or `blocked` unless the relevant production-capable route is recorded honestly.
`qa.status=pass` also requires `metadata.quality_target.tier=visual-acceptance-ready`.

Use `needs-review` or `blocked` when the background is only a reconstructed approximation, when core layers are missing, or when the result is mostly rectangular crops.

Per-object `quality_checks` should cover mask alignment, alpha edges, background residue, and reuse readiness. Missing mask or alpha provenance is a review blocker even when the PNG file opens correctly. Record `composition_order` so downstream renderers can rebuild the layer stack, and do not set package `qa.status` to `pass` unless every required object quality check is `pass`.

Use `record_quality_review.py` after inspecting previews to update `metadata.json` and append `qa_report.md` together. This prevents the common failure where imported layers remain `needs-review`, semantic analysis is missing, or `qa.status` is promoted without matching object-level evidence.
`candidate_promotion` is a formal approval gate, not a casual note. If a candidate asset replaces the current revision, the package should carry explicit candidate promotion evidence instead of relying on implicit QA status.
`final_promotion_acceptance` should be treated as a legacy alias in older packages only. New package state and current tooling should use `candidate_promotion` as the single canonical promotion gate.

Validation now requires both ordinary inspection previews from `build_previews.py` and quality previews from `build_quality_previews.py` for each reusable object layer. A package without preview evidence is incomplete even if the transparent PNGs and masks exist.

Run `audit_visual_quality.py` before final review to write `_staging/quality/quality_audit.json` and `_staging/quality/qa_audit_contact_sheet.png`. This audit only raises warnings such as `edge-halo`, `color-residue`, `detached-fragments`, `smear-artifact`, `over-flat-reconstruction`, `style-mismatch-reconstruction`, `hard-alpha-risk`, `support-layer-misclassified`, or `carrier-glyph-cross-contamination`. It does not replace manual review and does not set `qa.status=pass`.

Bbox/manual-estimated crop layers are draft-only unless explicitly confirmed. Use `record_quality_review.py --confirm-crop-layer --object-id <id>` only after a human accepts that layer for production reuse.

Approximate `background_clean.png` files and structural support plates should record `reconstruction_provenance` and remain `needs-review` unless the approximation has been explicitly accepted.

For high-risk repairs, stage candidates in `_staging/repair_candidates/`, compare them there, and promote the selected candidate with `promote_candidate_asset.py`. Do not silently overwrite package assets before candidate selection is recorded.

When staged candidates exist, run `describe_candidate_work_items.py` to write `_staging/repair_candidates/candidate_work_items.json`. It will tell you whether candidate stage is still empty, whether compare evidence is needed, whether a candidate selection is still pending after compare, whether a candidate is ready for promotion, or whether candidate work is already complete.

That report should also surface candidate provider ids when provider-stage manifests exist. If a staged candidate pool mixes providers, the next-step detail should say so explicitly before you run compare.

When a comparison record already contains `selected_candidate_id` and `selection_reason`, `promote_candidate_asset.py --comparison-id ...` can now reuse those values instead of forcing them to be repeated. If either one is still missing from the comparison evidence, promotion should continue to fail closed.

`describe_candidate_work_items.py` now also distinguishes between “candidate is selected” and “candidate promotion approval has been recorded.” If compare already chose a candidate but `metadata.confirmation.candidate_promotion` is still pending, the helper should recommend a `record_quality_review.py` formal-approval step before it recommends `promote_candidate_asset.py`.

If compare evidence exists but no selected candidate has been recorded yet, use `record_candidate_selection.py` to write `selected_candidate_id`, `selection_reason`, and a decision-log entry before approval or promotion. For a single-candidate compare set it may infer the candidate; for an ambiguous compare it must still require an explicit `--candidate-id`.

If you already know both the compare winner and whether promotion should continue, use `apply_candidate_selection_decision.py`. Its safe default is `--promotion-answer skip`, which records selection only. Switch that flag to `yes` or `no` when you want the same command to continue into the promotion-decision path.

`promote_candidate_asset.py` itself now enforces that same gate. Promotion should fail closed until `metadata.confirmation.candidate_promotion` is `confirmed` or explicitly `not-required` with a real user-backed source.

If you want a lower-burden way to record that approval, use `record_candidate_promotion_approval.py`. It can reuse compare-owned `selected_candidate_id` and `selection_reason`, or infer the candidate from a single-candidate compare set, then write the `candidate_promotion` gate through the normal review contract.

If you want one deterministic command that both records the yes/no decision and, for `yes`, continues into promotion, use `apply_candidate_promotion_decision.py`.

That adapter can now infer `delivery_class` from the planned route or current object delivery state in common cases, and it can generate a default `repair_note`. If the route truth is not strong enough, it should still fail closed and require an explicit `--delivery-class`.

If no compare evidence exists yet but the object has exactly one staged candidate, the same approval adapter and decision adapter can now use that direct single-candidate path. If more than one staged candidate exists, they must still stop and require an explicit compare or winner selection first.

If compare evidence or staged candidates are mixed across providers for the same object, both adapters may take `--provider-id` so they can resolve the correct provider-specific comparison or the unique staged candidate for that provider. If `--provider-id` still matches more than one comparison or more than one staged candidate, they should fail closed and require a more explicit user decision.

`describe_candidate_work_items.py` should now also show candidate provider ids when provider-stage manifests exist. If a staged candidate pool mixes providers, its next-step detail should say that explicitly before compare starts.

Use `compare_candidate_assets.py` when more than one viable repair candidate exists. The compare artifact is review evidence, not a final asset, and should stay in `_staging/repair_candidates/` or `_archive_intermediate/`. Compare is not just a contact sheet; the compare manifest should also record candidate asset paths, criteria, review focus, risks, and later selection rationale.

For generated candidate pools, the candidate work-item helper should now recommend the lower-burden compare command that matches the real auto-discovery rules: no manual `--candidate` list for a single-provider pool, `--provider-id <preferred>` when a valid generation provider preference safely scopes a mixed-provider pool, and an explicit `--provider-id <provider-id>` placeholder when no safe provider default exists.

When you summarize a run, call out the primary segmenter, the matting/refinement tool, and any helper-only tools separately. Pillow/OpenCV/skimage should only appear in the helper-tools bucket.

Use separate final-report lines for:

```text
Validation result: structural package valid
Visual quality result: needs-review / blocked
Production reusable assets: N
Draft candidate assets: N
Support-only layers: N
```
