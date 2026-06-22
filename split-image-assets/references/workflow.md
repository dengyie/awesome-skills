# Split Image Assets Workflow

## Purpose

Use this workflow to turn a single source image into a reusable asset package. Optimize for reusable files, clear provenance, inspectable previews, and honest QA status.

## Stages

1. Intake the source image and identify the desired output package directory.
2. Run `scripts/init_asset_package.py` if the package does not already exist.
3. Analyze before extraction:
   - source dimensions
   - main object
   - secondary objects
   - background type
   - object overlap
   - shadows
   - complex edge regions
   - likely manual-review risks
4. Write the object inventory into `metadata.json`.
5. Produce or collect reusable assets through AI image tools, segmentation tools, manual editing, or user-provided files.
6. Keep individual objects separate before creating grouped or preview outputs.
7. Generate previews with `scripts/build_previews.py`.
8. Validate the package with `scripts/validate_asset_package.py`.
9. Inspect previews and write the final QA status into `qa_report.md` and `metadata.json`.
10. Report the package path, final status, and any manual correction points.

## Status Meanings

- `pass`: structure is valid and inspection found no blocking reuse issue.
- `needs-review`: package is usable as a draft, but one or more assets need human inspection or correction.
- `blocked`: package cannot be treated as reusable until missing files or serious quality issues are resolved.

## Do Not

- Do not treat a 2x2 preview as the final asset.
- Do not merge separate objects into one layer unless the grouped layer is explicitly additional.
- Do not hide AI-assisted fills or uncertain edges.
- Do not claim the scripts extracted objects from the source image.

