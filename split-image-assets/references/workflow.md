# Split Image Assets Workflow

## Purpose

Use this runbook to decide when the split-image-assets workflow keeps moving and when it is allowed to stop for a human.

Default rule: continue in `Running` unless the next branch is a real `AwaitingDecision`, `AwaitingExternalBlocker`, or `AwaitingApproval` event. Progress-only pauses are not allowed.

## State Taxonomy

- `Running`: normal execution, evidence capture, packaging, previews, audits, validation
- `AwaitingDecision`: a user choice is required because different answers change package semantics
- `AwaitingExternalBlocker`: execution cannot continue without tools, outputs, installs, credentials, or another external prerequisite
- `AwaitingApproval`: the package has enough evidence to request a formal approval gate
- `Completed`: the current run has reached a terminal outcome

## Continue-Versus-Stop Rules

When a stage is in `Running`, keep going and report commentary only.

Stopping is allowed only when all of the following are true:

1. The stop maps to one of `AwaitingDecision`, `AwaitingExternalBlocker`, or `AwaitingApproval`.
2. The minimum evidence for that stop has been gathered.
3. Prior user instructions and recorded metadata do not already answer the question.

If pause is not allowed, continue with the documented fallback and record the rationale in metadata instead of stopping.

## Gate Runbook

### `tooling_preflight`

- Formal gate name: Preflight Tooling Recommendation Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingExternalBlocker`
- Minimum evidence before stop:
  - `scripts/check_extraction_environment.py` report captured
  - missing roles identified for detection, segmentation, alpha refinement/matting, or reconstruction
  - `production_capable`, `missing_for_production`, `missing_roles`, `recommended_installs`, and `why_it_matters` available
- Stop only when:
  - the workflow cannot honestly claim a production-capable path without a user choice or external outputs
- Continue behavior when pause is not allowed:
  - if prior instructions already select `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`, record that in `metadata.capability`, `metadata.confirmation.tooling_preflight`, and `metadata.decision_log[]`, then continue
  - if the environment is already production-capable, record the evidence and continue without stopping

### `granularity_alignment`

- Formal gate name: Granularity Alignment Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingDecision`
- Minimum evidence before stop:
  - semantic layer hierarchy analyzed
  - candidate split choices identified for granularity, text handling, carrier/glyph policy, background expectation, and layer independence
  - at least one branch would materially change reuse boundaries or downstream rebuild expectations
- Stop only when:
  - existing instructions and metadata do not already settle those branches
- Continue behavior when pause is not allowed:
  - if user intent is already durable, record `mode`, `scope_strategy`, `text_handling`, `carrier_glyph_policy`, `background_expectation`, `layer_independence`, `metadata.confirmation.granularity_alignment`, and a decision-log entry, then continue
  - if the image is straightforward and the split is clearly derivable, continue with the recorded rationale instead of asking again

### `pilot_object`

- Formal gate name: Pilot Object Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingApproval`
- Minimum evidence before stop:
  - image class is dense UI, dashboard, badge/tile/glyph, or another high-risk composition
  - one representative object has been selected as the pilot
  - the pilot’s granularity and cleanliness can be demonstrated with package evidence
- Stop only when:
  - widening extraction without pilot signoff would materially increase cleanup cost or semantic drift
- Continue behavior when pause is not allowed:
  - if prior user instruction or recorded policy makes the pilot `not-required`, record that in `metadata.confirmation.pilot_object` and continue with the broader batch
  - if the composition is simple, document why no pilot stop is needed and continue

### `approximate_reconstruction`

- Formal gate name: Approximate Reconstruction Acceptance Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingDecision`
- Minimum evidence before stop:
  - exact hidden pixels are unavailable
  - the layer would rely on inferred pixels, inpainting, manual redraw, or another approximate path
  - the package can describe the affected asset and the reconstruction provenance
- Stop only when:
  - approximate delivery would change truthfulness, quality claims, or downstream use
- Continue behavior when pause is not allowed:
  - if prior instructions already allow approximation, keep the asset classified as approximate, record `delivery_class=approximate-reconstruction`, `reconstruction_provenance`, `active_reconstruction_method`, `metadata.confirmation.approximate_reconstruction`, and continue
  - if approximation is not accepted, keep the layer `needs-review` or `blocked` and continue with the draft-honest path instead of stopping for a progress update

### `final_acceptance`

- Formal gate name: Final User Acceptance Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingApproval`
- Minimum evidence before stop:
  - required previews, quality previews, audit evidence, and QA review exist
  - requested granularity and cleanliness are visible in the current package
  - the package is otherwise ready for a final pass/needs-review decision
- Stop only when:
  - a formal user acceptance is required before claiming `qa.status=pass`
- Continue behavior when pause is not allowed:
  - if explicit user acceptance already exists, record `metadata.confirmation.final_acceptance` and continue to final reporting
  - if acceptance is absent, continue with `qa.status=needs-review` or `blocked`; do not stop merely to announce stage completion

### `candidate_promotion`

- Formal gate name: Candidate Promotion Acceptance Gate
- Default state: `Running`
- Pause allowed: yes
- Allowed pause category: `AwaitingApproval`
- Minimum evidence before stop:
  - a candidate asset is ready to replace the current revision
  - compare evidence or a direct-promotion rationale exists
  - the selected candidate and revision impact are known
- Stop only when:
  - replacing the current revision requires formal approval and no prior approved promotion rule already covers it
- Continue behavior when pause is not allowed:
  - if an existing accepted policy already authorizes the promotion, record `metadata.confirmation.candidate_promotion`, `selected_candidate_id`, `current_asset_revision`, `repair_history[]`, `candidate_comparisons[]`, and continue
  - if approval is absent, keep the candidate staged and continue with review evidence capture rather than promoting silently

## Standard Execution Path

1. Inspect or initialize the package.
2. Run `tooling_preflight`.
3. Select recipe and analyze semantic layers.
4. Run `granularity_alignment`.
5. Use a `pilot_object` when the composition is dense or high-risk.
6. Extract or import assets and masks.
7. If needed, resolve `approximate_reconstruction`.
8. Build previews, quality previews, audits, and QA evidence.
9. Validate structure and export the manifest.
10. Request `final_acceptance` and `candidate_promotion` only when the evidence actually supports those approval gates.

## Stop Hygiene

- Do not stop for progress-only pauses.
- Do not stop because a stage finished.
- Do not ask multiple unrelated questions in one stop.
- Do not ask for a decision that prior instructions already resolved.
- Do not convert commentary into a fake gate just to summarize work.
