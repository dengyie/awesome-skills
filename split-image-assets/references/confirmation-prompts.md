# Confirmation Prompts

Use this file as the allowed-stop template library for split-image-assets.

Every stop prompt must follow the grill-me-style exit contract:

- `Why This Needs a Human`
- `Recommendation`
- `Options and Impact`
- `What I Will Do After Confirmation`

- `explicit-user-confirmed`
- `inferred-from-user`

`inferred-from-user` means the answer is already supported by durable user evidence. It does not mean the agent guessed.

Progress updates are commentary, not confirmation gates.

## What Is Not A Confirmation Prompt

Do not stop and wait for:

- routine progress updates
- ordinary tool output summaries
- internal implementation checkpoints
- non-blocking uncertainty that does not change package truth

- `user-decision`
- `external-blocker`
- `formal-approval`

Pause category: `external-blocker` by default

Must ask when: tools or professional upstream outputs are still missing and no prior user-backed path already resolves the branch.

May infer when: the user already approved `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only` for the current run and that evidence can be cited.

Question: Production-quality asset splitting needs professional upstream tools. This environment is missing [missing capabilities/tools]. Should I pause so you can install/activate them, use external segmented assets/masks, or continue as draft-packaging-only?

- `user-decision` -> `AwaitingDecision`
- `external-blocker` -> `AwaitingExternalBlocker`
- `formal-approval` -> `AwaitingApproval`

These prompts must not be used for progress-only pauses.

Medium/high-risk semantic divergence is not its own stop class. If it truly requires a human branch choice, it must still use `user-decision`.

Pause category: `user-decision`

Must ask when: different answers would materially change asset boundaries, text handling, carrier/glyph behavior, or layer independence.

May infer when: existing user instructions or approved metadata already settle those branches.

Question: Should this package target module, component, atomic-layer, or production-editable reconstruction granularity?

These are the only retained allowed-stop templates:

| Gate id | Formal gate name | Stop class | State |
| --- | --- | --- | --- |
| `tooling_preflight` | Preflight Tooling Recommendation Gate | `external-blocker` | `AwaitingExternalBlocker` |
| `granularity_alignment` | Granularity Alignment Gate | `user-decision` | `AwaitingDecision` |
| `pilot_object` | Pilot Object Gate | `formal-approval` | `AwaitingApproval` |
| `approximate_reconstruction` | Approximate Reconstruction Acceptance Gate | `user-decision` | `AwaitingDecision` |
| `final_acceptance` | Final Acceptance Gate | `formal-approval` | `AwaitingApproval` |
| `candidate_promotion` | Candidate Promotion Acceptance Gate | `formal-approval` | `AwaitingApproval` |

There is no separate `Final Promotion Acceptance Gate`. Final package signoff uses `final_acceptance`. Replacing the current asset revision uses `candidate_promotion`.

Pause category: `formal-approval`

Must ask when: dense UI or approximate reconstruction work should not widen without a pilot signoff.

May infer when: a prior accepted policy explicitly marks the current case as `not-required`.

Question: Before I continue with the broader batch, should I use this representative object as a pilot and wait for your confirmation on granularity and cleanliness?

- Forbid progress-only pauses.
- Forbid stage-complete pauses.
- Forbid multiple unrelated questions in one stop.
- Forbid asks already resolved by prior user instructions or recorded metadata.

If the workflow only needs to report status, keep running and send commentary instead of using a stop prompt.

## Prompt Shape

Pause category: `user-decision`

Question: Should this icon or badge be split into a carrier tile and foreground glyph?

- stop class
- state
- stop condition
- recommended answer style
- effect on metadata

## Retained Prompt Templates

### `tooling_preflight`

Pause category: `user-decision`

Question: Should text, labels, buttons, or UI chrome be extracted as image layers or rebuilt downstream as live UI/text?

Prompt body:

- `Why This Needs a Human`: Production-capable extraction is blocked until the run path is chosen.
- `Recommendation`: Prefer `install-or-activate-tools` or `external-professional-outputs` when the goal is production reuse.
- `Options and Impact`:
  - `install-or-activate-tools`: highest quality path, but waits on environment changes
  - `external-professional-outputs`: keeps the workflow moving if reliable upstream assets exist
  - `draft-packaging-only`: continues now, but the package must remain draft-honest
- `What I Will Do After Confirmation`: Record the chosen path in metadata and either continue with production-capable evidence or keep the package in draft-only status.

### `granularity_alignment`

Pause category: `user-decision` first, `formal-approval` before pass-claim escalation

Question: Is an approximate reconstructed background or support plate acceptable for this package?

Prompt body:

- `Why This Needs a Human`: Different split choices would produce materially different asset boundaries and downstream editing behavior.
- `Recommendation`: Prefer `atomic-layer` for reusable UI assets and `production-editable` when downstream rebuild matters.
- `Options and Impact`:
  - `component`: faster draft review, less downstream flexibility
  - `atomic-layer`: better reuse, recolor, animation, and inspection
  - `production-editable`: strongest downstream rebuild path, more scope up front
- `What I Will Do After Confirmation`: Record the chosen split policy and continue extraction without reopening the same branch later.

### `pilot_object`

Pause category: `user-decision` only when the answer changes deliverable truth; otherwise continue and report commentary.

Question: Should this low-confidence mask be retried with another upstream tool, sent to manual review, or retained as draft-only evidence?

Prompt body:

- `Why This Needs a Human`: Widening the batch before pilot approval risks scaling the wrong split or cleanup standard.
- `Recommendation`: Approve the pilot only when its granularity and cleanliness match the target package quality.
- `Options and Impact`:
  - `approved`: continue the wider batch with the pilot as the reference standard
  - `revise-and-retry`: hold the batch, improve the pilot, and recheck
  - `not-required`: continue without a pilot stop because the composition or prior policy makes it unnecessary
- `What I Will Do After Confirmation`: Either proceed with the broader batch, keep work focused on the pilot, or record that no pilot gate is needed.

### `approximate_reconstruction`

Pause category: `formal-approval`

Question: Does the current package meet the requested granularity and cleanliness well enough to mark `qa.status=pass`?

Prompt body:

Decision effect: Only promote to `pass` after required quality checks pass and the acceptance decision is recorded.

## Candidate Promotion Acceptance

Pause category: `formal-approval`

Must ask when: a candidate asset is about to replace the current revision and no prior approved promotion rule covers the replacement.

May infer when: a prior accepted policy explicitly authorizes promotion under the same compare/direct-promotion conditions and that evidence can be cited.

Question: Should candidate X replace the current revision for this object?

Recommended answer: Yes only after compare evidence or a direct-promotion rationale exists.

Decision effect: Record `metadata.confirmation.candidate_promotion`, update `selected_candidate_id`, `current_asset_revision`, `repair_history[]`, and keep the selection rationale durable.
