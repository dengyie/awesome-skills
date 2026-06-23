# QA Standards

## Structure

- Required directories and files exist.
- `metadata.json` is parseable and references existing files.
- `metadata.analysis.visual_hierarchy` names semantic layers, not just crop regions.
- `metadata.analysis.recommended_split_plan` explains reusable layer boundaries.
- `metadata.extraction_pipeline` names the recipe, ordered stages, upstream tools, and quality gates.
- Object PNGs that represent cutouts have an alpha channel.
- Object metadata records `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`.
- Source-space masks match source dimensions.
- Inspection previews and segmentation-quality previews exist for every reusable object layer.
- `qa_report.md` contains a final status.

## Semantic Layer Quality

Check that assets follow the image's meaning:

- background/backplate is separate from foreground objects
- primary subjects are separate from labels, route lines, controls, or decorations when those layers need independent reuse
- grouped layers are additional convenience assets, not replacements for individual layers
- rectangular crops are only tight storage bounds around source-space masks

If a package mostly contains page rectangles, grid slices, or bounding boxes, mark it `blocked` or `needs-review` even if the files validate structurally.

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

## Segmentation Quality Gates

Record these checks per reusable layer:

- `mask_alignment`: mask follows the intended semantic boundary and is not just a rectangular crop
- `alpha_edges`: transparent edges preserve hair, glow, glass, smoke, softness, or hard silhouettes as appropriate
- `background_residue`: cutout does not carry visible unwanted background pixels or halos
- `reuse_readiness`: layer can be composited on a new background without obvious extraction artifacts

Mark any unknown, weak, or tool-only inspection as `needs-review`. Use `blocked` when core subject boundaries are wrong or when the package cannot identify how masks and alpha were produced.

Allowed object check values are `pass`, `needs-review`, `blocked`, and `unknown`. The package-level `qa.status` cannot be `pass` unless every required object quality check is `pass`.

## Quality Preview Evidence

Run `scripts/build_quality_previews.py` after assets and masks are present. Inspect:

- mask overlay against the original source image
- alpha inspection on a checkerboard background
- ordinary white-background and checkerboard previews from `build_previews.py`
- layer stack order through `composition_order`

Quality previews are evidence, not proof. They help reviewers identify edge and mask failures quickly.

Structural validation requires these preview references to exist. Missing preview evidence means the package has not completed the QA loop, even when object files and masks are present.

## Background Repair

Check `background_clean.png` for:

- ghost silhouettes
- repeated texture artifacts
- broken perspective
- inconsistent lighting
- obvious fill seams
- impossible hidden-pixel recovery being claimed as exact

## Provenance

Record which parts are exact extraction, AI-assisted generation, manual editing, estimated geometry, or unknown. Low-confidence or AI-assisted work should carry manual-review flags unless a human has inspected it.

When a layer is reconstructed rather than extracted, record that explicitly. A reconstructed route, backplate, or missing background can be useful, but it is not an exact extraction.
