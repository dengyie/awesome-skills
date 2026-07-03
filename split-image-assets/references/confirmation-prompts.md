# Confirmation Prompts

Use this file as the allowed-stop template library for split-image-assets.

Every stop prompt must follow the grill-me-style exit contract:

- `Why This Needs a Human`
- `Recommendation`
- `Options and Impact`
- `What I Will Do After Confirmation`

Only three stop classes are allowed:

- `user-decision`
- `external-blocker`
- `formal-approval`

Those stop classes map to workflow states like this:

- `user-decision` -> `AwaitingDecision`
- `external-blocker` -> `AwaitingExternalBlocker`
- `formal-approval` -> `AwaitingApproval`

These prompts must not be used for progress-only pauses.

Medium/high-risk semantic divergence is not its own stop class. If it truly requires a human branch choice, it must still use `user-decision`.

## Normalized Gate Taxonomy

These are the only retained allowed-stop templates:

| Gate id | Formal gate name | Stop class | State |
| --- | --- | --- | --- |
| `tooling_preflight` | Preflight Tooling Recommendation Gate | `external-blocker` | `AwaitingExternalBlocker` |
| `granularity_alignment` | Granularity Alignment Gate | `user-decision` | `AwaitingDecision` |
| `generation_routing` | Generation Routing Gate | `user-decision` | `AwaitingDecision` |
| `pilot_object` | Pilot Object Gate | `formal-approval` | `AwaitingApproval` |
| `approximate_reconstruction` | Approximate Reconstruction Acceptance Gate | `user-decision` | `AwaitingDecision` |
| `final_acceptance` | Final Acceptance Gate | `formal-approval` | `AwaitingApproval` |
| `candidate_promotion` | Candidate Promotion Acceptance Gate | `formal-approval` | `AwaitingApproval` |

There is no separate `Final Promotion Acceptance Gate`. Final package signoff uses `final_acceptance`. Replacing the current asset revision uses `candidate_promotion`.

## Explicit Prohibitions

- Forbid progress-only pauses.
- Forbid stage-complete pauses.
- Forbid multiple unrelated questions in one stop.
- Forbid asks already resolved by prior user instructions or recorded metadata.

If the workflow only needs to report status, keep running and send commentary instead of using a stop prompt.

## Prompt Shape

Each retained prompt should include:

- stop class
- state
- stop condition
- recommended answer style
- effect on metadata

## Retained Prompt Templates

### `tooling_preflight`

- Formal gate name: Preflight Tooling Recommendation Gate
- Stop class: `external-blocker`
- State: `AwaitingExternalBlocker`
- Stop condition:
  - the preflight report shows missing tooling or missing professional upstream outputs, and no prior user-backed path already resolves the branch
- Recommended answer style:
  - choose one explicit path: `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`
- Effect on metadata:
  - update `metadata.capability`
  - update `metadata.confirmation.tooling_preflight`
  - append `metadata.decision_log[]`

Prompt body:

- `Why This Needs a Human`: Production-capable extraction is blocked until the run path is chosen.
- `Recommendation`: Prefer `install-or-activate-tools` or `external-professional-outputs` when the goal is production reuse.
- `Options and Impact`:
  - `install-or-activate-tools`: highest quality path, but waits on environment changes
  - `external-professional-outputs`: keeps the workflow moving if reliable upstream assets exist
  - `draft-packaging-only`: continues now, but the package must remain draft-honest
- `What I Will Do After Confirmation`: Record the chosen path in metadata and either continue with production-capable evidence or keep the package in draft-only status.

### `granularity_alignment`

- Formal gate name: Granularity Alignment Gate
- Stop class: `user-decision`
- State: `AwaitingDecision`
- Stop condition:
  - the split boundary, text handling, carrier/glyph policy, or layer independence would materially change reuse semantics and existing instructions do not already decide it
- Recommended answer style:
  - choose one durable granularity policy such as `component`, `atomic-layer`, or `production-editable`, plus any required text/background preferences
- Effect on metadata:
  - update `metadata.granularity.mode`
  - update `metadata.granularity.scope_strategy`
  - update `metadata.granularity.text_handling`
  - update `metadata.granularity.carrier_glyph_policy`
  - update `metadata.granularity.background_expectation`
  - update `metadata.granularity.layer_independence`
  - update `metadata.confirmation.granularity_alignment`
  - append `metadata.decision_log[]`

Prompt body:

- `Why This Needs a Human`: Different split choices would produce materially different asset boundaries and downstream editing behavior.
- `Recommendation`: Prefer `atomic-layer` for reusable UI assets and `production-editable` when downstream rebuild matters.
- `Options and Impact`:
  - `component`: faster draft review, less downstream flexibility
  - `atomic-layer`: better reuse, recolor, animation, and inspection
  - `production-editable`: strongest downstream rebuild path, more scope up front
- `What I Will Do After Confirmation`: Record the chosen split policy and continue extraction without reopening the same branch later.

### `generation_routing`

- Formal gate name: Generation Routing Gate
- Stop class: `user-decision`
- State: `AwaitingDecision`
- Stop condition:
  - a planned object sits in the ambiguous generate band, a protected object would otherwise route to `generate`, or the route switch would materially change delivery truth claims
- Recommended answer style:
  - choose one route for the named object: `extract`, `reconstruct`, `generate`, `rebuild_downstream`, or `support_only`
- Effect on metadata:
  - update `plan_manifest.json`
  - update `metadata.confirmation.generation_routing`
  - append an object-scoped `metadata.decision_log[]` entry for the generated object branch
  - append `metadata.decision_log[]`

Prompt body:

- `Why This Needs a Human`: This object is at the boundary where the workflow could either keep trying extraction or switch to a different delivery truth class.
- `Recommendation`: Prefer `generate` only when the object is reconstruction-like, source recovery is weak, and the package can remain honest about generated delivery.
- `Options and Impact`:
  - `extract`: preserve extraction semantics, but may cost more cleanup effort
  - `reconstruct`: stay source-constrained, but accept approximate repair discipline
  - `generate`: move to generated-reconstruction candidate flow with stricter evidence and approval
  - `rebuild_downstream`: avoid raster work for rebuildable content
  - `support_only`: keep the object as support or context, not a production atomic asset
- `What I Will Do After Confirmation`: Record the chosen route, keep the package truthful about that route, and continue only with the evidence path that matches it.

### `pilot_object`

- Formal gate name: Pilot Object Gate
- Stop class: `formal-approval`
- State: `AwaitingApproval`
- Stop condition:
  - a dense or high-risk composition should not widen beyond the pilot until the representative object is accepted
- Recommended answer style:
  - answer with `approved`, `revise-and-retry`, or `not-required`
- Effect on metadata:
  - update `metadata.confirmation.pilot_object`
  - append `metadata.decision_log[]` when the pilot materially changes batch scope

Prompt body:

- `Why This Needs a Human`: Widening the batch before pilot approval risks scaling the wrong split or cleanup standard.
- `Recommendation`: Approve the pilot only when its granularity and cleanliness match the target package quality.
- `Options and Impact`:
  - `approved`: continue the wider batch with the pilot as the reference standard
  - `revise-and-retry`: hold the batch, improve the pilot, and recheck
  - `not-required`: continue without a pilot stop because the composition or prior policy makes it unnecessary
- `What I Will Do After Confirmation`: Either proceed with the broader batch, keep work focused on the pilot, or record that no pilot gate is needed.

### `approximate_reconstruction`

- Formal gate name: Approximate Reconstruction Acceptance Gate
- Stop class: `user-decision`
- State: `AwaitingDecision`
- Stop condition:
  - exact hidden pixels are unavailable and accepting approximation would change truthfulness or downstream use
- Recommended answer style:
  - answer explicitly whether approximation is acceptable for the named layer and intended use
- Effect on metadata:
  - update `metadata.confirmation.approximate_reconstruction`
  - record `delivery_class=approximate-reconstruction`
  - record `reconstruction_provenance`
  - record `active_reconstruction_method`
  - append `metadata.decision_log[]`

Prompt body:

- `Why This Needs a Human`: The workflow can continue, but it cannot honestly treat an inferred reconstruction as exact without user acceptance.
- `Recommendation`: Accept approximation only when the package can remain honest about the layer being approximate.
- `Options and Impact`:
  - `accept approximation`: continue with an approximate layer that may remain `needs-review`
  - `reject approximation`: keep the layer blocked or draft-only until a better path exists
- `What I Will Do After Confirmation`: Either record the approximate path and continue, or keep the package honest by leaving that layer unpromoted.

### `final_acceptance`

- Formal gate name: Final Acceptance Gate
- Stop class: `formal-approval`
- State: `AwaitingApproval`
- Stop condition:
  - the package has enough evidence for a final pass claim, but formal user acceptance is still required
- Recommended answer style:
  - answer with `accept`, `keep-needs-review`, or a short correction directive tied to the current package state
- Effect on metadata:
  - update `metadata.confirmation.final_acceptance`
  - append `metadata.decision_log[]`
  - allow or deny promotion to final `qa.status=pass`

Prompt body:

- `Why This Needs a Human`: Marking the package as accepted changes the final delivery claim, not just the workflow status.
- `Recommendation`: Keep `needs-review` unless the current granularity, cleanliness, and reconstructed regions are acceptable as delivered.
- `Options and Impact`:
  - `accept`: allows final acceptance metadata and a pass claim if all other evidence is green
  - `keep-needs-review`: preserves an honest draft or review-required outcome
  - `correction directive`: identifies what must change before another acceptance request
- `What I Will Do After Confirmation`: Either finalize the package state or continue with the recorded review outcome.

### `candidate_promotion`

- Formal gate name: Candidate Promotion Acceptance Gate
- Stop class: `formal-approval`
- State: `AwaitingApproval`
- Stop condition:
  - a candidate asset is about to replace the current revision and no prior approved rule already covers that promotion
- Recommended answer style:
  - answer with `promote <candidate-id>`, `keep current`, or a comparison-based correction note
- Effect on metadata:
  - update `metadata.confirmation.candidate_promotion`
  - update `selected_candidate_id`
  - update `current_asset_revision`
  - update `repair_history[]`
  - update `candidate_comparisons[]`
  - append `metadata.decision_log[]`

Prompt body:

- `Why This Needs a Human`: Promotion changes the current package-owned revision and should not happen implicitly.
- `Recommendation`: Promote only when compare evidence or a direct-promotion rationale supports the replacement.
- `Options and Impact`:
  - `promote <candidate-id>`: replaces the current revision and records the selection rationale
  - `keep current`: leaves the existing revision in place and preserves the candidate as evidence only
  - `correction note`: requests another candidate pass before any promotion
- `What I Will Do After Confirmation`: Either promote the selected candidate with durable metadata or keep the current revision unchanged.
