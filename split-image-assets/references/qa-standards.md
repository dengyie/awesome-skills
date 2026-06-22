# QA Standards

## Structure

- Required directories and files exist.
- `metadata.json` is parseable and references existing files.
- Object PNGs that represent cutouts have an alpha channel.
- Source-space masks match source dimensions.
- `qa_report.md` contains a final status.

## Proportion

- Individual assets preserve the object's aspect ratio.
- Grouped outputs preserve relative scale when that relationship is important.
- Preview layout may center objects, but must not imply that preview scale is source truth unless metadata says so.

## Edge Quality

Check for:

- jagged edges
- halos
- colored fringes
- background residue
- overly hard edges on fuzzy objects
- destroyed transparency on glass, smoke, reflections, or translucent materials

## Background Repair

Check `background_clean.png` for:

- ghost silhouettes
- repeated texture artifacts
- broken perspective
- inconsistent lighting
- obvious fill seams

## Provenance

Record which parts are exact extraction, AI-assisted generation, manual editing, estimated geometry, or unknown. Low-confidence or AI-assisted work should carry manual-review flags unless a human has inspected it.

