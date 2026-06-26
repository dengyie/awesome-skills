# QA Standards

## Structure

- Required directories and files exist.
- `metadata.json` is parseable and references existing files.
- `metadata.analysis.visual_hierarchy` names semantic layers, not just crop regions.
- `metadata.analysis.recommended_split_plan` explains reusable layer boundaries.
- `metadata.decision_log[]` records subjective confirmation decisions when they affect reuse, editability, approximate reconstruction, or final delivery claims.
- `metadata.extraction_pipeline` names the recipe, ordered stages, upstream tools, and quality gates.
- Object PNGs that represent cutouts have an alpha channel.
- Object metadata records `layer_kind`, `composition_order`, `semantic_boundary`, `mask_source`, `alpha_source`, and `quality_checks`.
- Object metadata records `asset_class` and `reuse_status` so candidate, support, blocked, and production-ready layers cannot be confused.
- `metadata.asset_summary` separates production-ready assets, draft candidate assets, support-only layers, and blocked assets.
- Source-space masks match source dimensions.
- Inspection previews and segmentation-quality previews exist for every reusable object layer.
- `qa_report.md` contains a final status.
- Intermediate external outputs are kept in `_staging/` or `_archive_intermediate/`, not loose in the package root.

## Semantic Layer Quality

Check that assets follow the image's meaning:

- background/backplate is separate from foreground objects
- primary subjects are separate from labels, route lines, controls, or decorations when those layers need independent reuse
- grouped layers are additional convenience assets, not replacements for individual layers
- rectangular crops are only tight storage bounds around source-space masks
- UI icon-in-tile, badge-in-card, and glyph-on-plate elements are split into carrier and glyph layers when independent reuse or edge cleanup requires it

If a package mostly contains page rectangles, grid slices, or bounding boxes, mark it `blocked` or `needs-review` even if the files validate structurally.

If a reusable layer uses a bbox, crop, or manual-estimated crop mask, keep the package `needs-review` or `blocked` until a human confirms that exact layer as production-acceptable. Record that confirmation with `record_quality_review.py --confirm-crop-layer`.

For draft-only packages, candidate PNG count is not production asset count. Report `not production reusable`, keep `production-ready assets: 0` unless real production-capable evidence exists, and count unreviewed cutouts as draft candidate assets.

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

For subjective visual decomposition, do not promote `qa.status` to `pass` just because structural validation succeeds. Final `pass` also needs an explicit or recorded user acceptance decision for the requested granularity, cleanliness, and approximate reconstructed regions.

## Quality Preview Evidence

Run `scripts/build_quality_previews.py` after assets and masks are present. Inspect:

- mask overlay against the original source image
- alpha inspection on a checkerboard background
- ordinary white-background and checkerboard previews from `build_previews.py`
- layer stack order through `composition_order`

Quality previews are evidence, not proof. They help reviewers identify edge and mask failures quickly.

Structural validation requires these preview references to exist. Missing preview evidence means the package has not completed the QA loop, even when object files and masks are present.

The validator checks evidence and honesty, not visual beauty. Use preview evidence plus human or user confirmation to resolve subjective quality and granularity decisions.

Source-space masks are normal QA artifacts. A small UI component can produce a mostly black mask with a small white region because the mask is aligned to the original source image, not cropped to the asset bbox.

Run `scripts/audit_visual_quality.py` before final review when possible. Treat its findings as warnings that focus manual attention, not automatic pass/fail decisions. Typical warning codes include:

- `edge-halo`
- `color-residue`
- `detached-fragments`
- `smear-artifact`
- `over-flat-reconstruction`
- `style-mismatch-reconstruction`
- `hard-alpha-risk`
- `support-layer-misclassified`
- `carrier-glyph-cross-contamination`

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

Approximate background clean plates and structural support layers must record `reconstruction_provenance`. Keep them `needs-review` unless a human explicitly confirms the approximation is acceptable for the requested downstream use.

## Final Quality Report

Separate structural validity from visual readiness:

```text
Validation result: structural package valid / structurally invalid
Visual quality result: pass / needs-review / blocked
Production reusable assets: N
Draft candidate assets: N
Support-only layers: N
Blocked assets: N
```

Also report expected semantic layers, extracted layers, missing layers, grouped-but-not-atomic layers, downstream rebuild layers, and approximate layers.
