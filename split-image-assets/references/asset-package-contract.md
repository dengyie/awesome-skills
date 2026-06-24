# Asset Package Contract

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
  asset_manifest.json
  metadata.json
  qa_report.md
  _staging/
  _archive_intermediate/
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
- `capability.production_capable`
- `capability.missing_for_production`
- `capability.user_choice`
- `capability.notes`
- `decision_log`
- `extraction_pipeline.recipe`
- `extraction_pipeline.stages`
- `extraction_pipeline.quality_gates`
- `extraction_pipeline.tools`
- `objects`
- `previews`
- `qa.status`

`analysis.visual_hierarchy` must name the semantic layer stack from background to foreground. `analysis.recommended_split_plan` must describe the reusable layer boundaries. Rectangular crop plans do not satisfy this field unless each rectangle is only a tight bbox around a semantic mask.

`granularity` records the agreed split scope for the run. Use values such as `module`, `component`, `atomic-layer`, `production-editable`, or `draft`. `user_confirmed` records whether the user explicitly aligned on that granularity, and `notes` captures any nuance such as live text rebuild or approximate background acceptance.

`capability` records the tooling preflight result before extraction. `production_capable` is true only when mature upstream extraction capability or equivalent professional external evidence is available. `missing_for_production` lists missing upstream roles/tools such as `SAM2 or grounded detector` or `matting/refinement`. `user_choice` records `install-or-activate-tools`, `external-professional-outputs`, `draft-packaging-only`, `production-capable`, or `unset`. `notes` explains the quality implication of the choice.

`qa.status=pass` requires `capability.production_capable: true`. Draft-only or unrecorded tooling preflight must stay `needs-review` or `blocked` until production-capable upstream evidence or professional external outputs are recorded.

`decision_log` records confirmation-driven workflow decisions that materially affect reuse, editability, localization, reconstruction acceptance, or final delivery claims. Each entry must include:

- `stage`
- `question`
- `recommended_answer`
- `user_answer`
- `decision_effect`

If prior user instructions or existing metadata already answer the question, record that inferred decision instead of asking again. Do not leave subjective split choices only in chat.

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
- `quality_checks.mask_alignment`
- `quality_checks.alpha_edges`
- `quality_checks.background_residue`
- `quality_checks.reuse_readiness`
- `manual_review_flags`
- `manual_review_confirmed` when a crop-only or estimated layer is manually approved for production reuse
- `approximate` and `reconstruction_provenance` when a layer was reconstructed, inpainted, or approximated rather than extracted exactly

## Pipeline Contract

`extraction_pipeline` records how the package was produced. Use `grounded-segmentation-matting-repair` for a Grounded-SAM/SAM2 style mask pipeline followed by matting and background repair. Use `layered-rgba-decomposition` for Qwen-Image-Layered style multi-layer proposals.

The ordered `stages` list must include `semantic-analysis`, `segmentation`, `alpha-refinement`, `layer-packaging`, and `qa-review`. Add `detection`, `background-repair`, `layered-decomposition`, or `recursive-layer-review` when those stages are used.

`quality_gates` should name the checks performed before final status. `tools` must record external models, services, manual editing, or user-provided assets as objects with `name`, `role`, and `version` when known. Use `"unknown"` for a version only when the tool version cannot be recovered.

`qa.status` can be `pass`, `needs-review`, or `blocked`. Do not use `pass` when any required object `quality_checks` value is `needs-review`, `blocked`, or `unknown`.

## Production Assets Versus Previews

Transparent object PNGs, masks, and cleaned backgrounds are production assets.

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

For UI icon-in-tile, badge-in-card, or glyph-on-plate structures, prefer separate semantic layers such as `status_row_02_icon_tile` and `status_row_02_icon_glyph` when downstream reuse or edge cleanup benefits from that separation.

Structural validation does not prove visual perfection. It proves the package has enough pipeline and quality evidence for a human or downstream agent to inspect segmentation quality.

## External Tool Import Contract

Use `scripts/import_external_assets.py` when importing outputs from SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, manual editing, or user-provided files. The importer copies files into package-controlled `assets/` and `masks/` paths and records upstream tool provenance in `metadata.extraction_pipeline.tools`.

Imported layers default to `needs-review` quality checks because external generation is not the same as inspected production readiness.

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
- `extraction_pipeline.quality_gates`
- object-level `quality_checks`
- package `qa.status`
- review notes in `qa_report.md`

The script rejects `qa.status=pass` unless every required object quality check is already `pass` or is updated to `pass` in the same command.

## Intermediate Archive Contract

Use `scripts/archive_intermediates.py` when moving retained `_staging/` outputs into `_archive_intermediate/<run-id>/`. The helper writes `archive_manifest.json` so future reviewers can see which upstream candidate masks, temporary manifests, or refinement outputs were retained.
