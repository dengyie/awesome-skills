# Handoff

## Objective
- Prepare `split-image-assets` for manual testing after the mature-pipeline refactor.

## Current State
- The skill is implemented as a deterministic package, provenance, preview, validation, and manifest layer.
- It does not vendor or run SAM2, rembg, BiRefNet, RMBG, Qwen-Image-Layered, LayerDiffuse, inpainting, or generation directly.
- External mature tools produce pixels; `import_external_assets.py` imports those outputs into the package contract.
- `metadata.json` is the source of truth. `asset_manifest.json` is generated downstream handoff data.
- Initialized packages are expected to fail final validation until semantic analysis, extraction pipeline metadata, object inventory, quality checks, and previews are recorded.
- Ambiguous product/design split choices must pause and ask the user one focused question with a recommended answer.

## Read First
- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/pipeline-recipes.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/references/qa-standards.md`
- `docs/usage/split-image-assets.md`
- `docs/superpowers/specs/2026-06-23-split-image-assets-pipeline-refactor-design.md`

## Current Logic Map
- `scripts/init_asset_package.py`: creates package directories, copies the source image, writes starter metadata, and initializes `qa_report.md`.
- `scripts/import_external_assets.py`: copies external transparent assets and masks into package-owned paths, updates object metadata, records extraction pipeline recipe/stages/tools, and defaults quality checks to `needs-review`.
- `scripts/build_previews.py`: creates standard inspection previews and rejects package path escapes.
- `scripts/build_quality_previews.py`: creates mask overlay and alpha inspection evidence, rejects package path escapes, and fails if no QA previews are produced.
- `scripts/record_quality_review.py`: records semantic analysis, quality gates, per-object quality checks, package QA status, and `qa_report.md` notes after manual or agent inspection. It refuses `qa.status=pass` unless every required object quality check is `pass`.
- `scripts/validate_asset_package.py`: enforces structure, semantic analysis, extraction pipeline provenance, non-empty object inventory, alpha/mask requirements, object quality evidence, safe paths, preview consistency, and `qa.status` consistency.
- `scripts/export_asset_manifest.py`: writes downstream `asset_manifest.json` sorted by `composition_order` from `metadata.json`.

## Manual Test Sequence
```powershell
python split-image-assets\scripts\init_asset_package.py source.png output-package
python split-image-assets\scripts\import_external_assets.py output-package --object-id main_object --role main --layer-kind primary-subject --composition-order 10 --semantic-boundary "Main subject from upstream mask" --asset main.png --mask mask_main.png --mask-source sam2 --alpha-source rembg --tool-name SAM2 --tool-role segmentation --tool-version external
python split-image-assets\scripts\build_previews.py output-package
python split-image-assets\scripts\build_quality_previews.py output-package
python split-image-assets\scripts\record_quality_review.py output-package --visual-hierarchy background --visual-hierarchy "main object" --recommended-split-plan "Keep the main object separate from the background." --quality-gate "mask overlay inspected" --object-id main_object --mask-alignment pass --alpha-edges pass --background-residue pass --reuse-readiness pass --qa-status pass --review-note "Manual inspection accepted the imported layer."
python split-image-assets\scripts\validate_asset_package.py output-package
python split-image-assets\scripts\export_asset_manifest.py output-package
```

## Expected Test Signals
- Fresh initialized packages should fail validation until required analysis and evidence are added.
- Imported layers should start as `needs-review`.
- Quality checks and final QA status should be upgraded with `record_quality_review.py` after preview inspection, not by hand-editing disconnected files.
- `qa.status=pass` should fail if any required object quality check is not `pass`.
- Absolute paths and `..` path escapes should fail validation.
- The final package should include reusable PNG assets, masks, previews, quality previews, `metadata.json`, `qa_report.md`, and `asset_manifest.json`.

## Blockers
- GitHub publish is still manual-required: `gh auth status` reports the token for account `dengyie` is invalid. Run `gh auth login -h github.com`, then `git push origin main`.

## Validation To Run
```powershell
$env:PYTHONUTF8='1'; python -m unittest discover split-image-assets\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover tests -v
$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets
git diff --check
```
