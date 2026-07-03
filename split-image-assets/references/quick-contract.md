# Split Image Assets Quick Contract

Use this file as the short package contract view. Read this first when you need the fast rules. Read `asset-package-contract.md` when you need the full field-by-field contract.

## Execution

- Continue by default.
- Only three formal stop classes may pause execution:
  - `user-decision`
  - `external-blocker`
  - `formal-approval`
- Medium/high-risk semantic divergence is not a fourth class. If it truly requires a human branch choice, it must still use `user-decision`.
- Progress updates are commentary, not confirmation gates.

## Asset Routing

- Use an editability-first bias.
- Ordinary text, button labels, numeric values, and form values default to `rebuild_downstream`.
- Logo wordmarks, decorative text, and other fidelity-critical text may route to `extract_asset`.
- Ambiguous high-complexity text-like objects may route to `requires_user_confirmation`.
- `rebuild_downstream` objects should keep a placeholder/object record in metadata, but should not publish a production raster asset.

## Formal State Surfaces

- The formal state surfaces are `metadata.decision_log[]` and `metadata.confirmation`.
- They record real decisions, approvals, blockers, and evidence-backed inferred user intent.
- They must not contain progress updates, routine commentary, or stage-complete summaries.
- `agent-defaulted` is not legal for formal gate state.
- Use `metadata.confirmation.candidate_promotion` as the canonical promotion gate.
- Treat `final_promotion_acceptance` only as a legacy read-compatibility alias for older packages.

## Package Truth Rules

- `qa.status=pass` requires an honest production-capable path.
- non-generated reusable layers require extraction-capable `metadata.capability.production_capable=true`.
- generated-only pass paths require `metadata.capability.generation.production_ready=true` plus object-scoped generation-routing evidence.
- generated-only pass paths also require generated-object promotion or acceptance evidence; generation capability and route confirmation alone are not enough.
- `qa.status=pass` requires `quality_target.tier=visual-acceptance-ready`.
- `qa.status=pass` requires passing required object checks and the necessary confirmation state.
- Approximate or reconstructed layers must stay explicitly approximate.
- generated-reconstruction must stay explicitly generated and must not masquerade as clean extraction.
- Draft-only packages must stay draft-honest.

## Honest Counting

- Report `production-ready assets` separately.
- Report `draft candidate assets` separately.
- Report `support-only layers` separately.
- Report `blocked assets` separately.
- Do not count grouped support layers, approximate clean plates, or draft candidates as production-ready assets.
