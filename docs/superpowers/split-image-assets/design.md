# Split Image Assets Unified Agent-First Design

Date: 2026-06-29
Status: Canonical design for ongoing `split-image-assets` development
Target package: `split-image-assets`

## Authority

This is the single governing design document for the current `split-image-assets` refactor line.

It supersedes all earlier split-image-assets design docs that previously lived under dated `docs/superpowers/specs/` paths.

If a lower-level doc, package reference, script default, or test expectation conflicts with this document, this document wins and the implementation should be brought back into alignment.

## Goal

Refactor `split-image-assets` into an agent-first asset-splitting workflow with three properties:

1. execution continues by default
2. raster extraction only happens when the object has real visual asset value
3. formal state, metadata, tooling, and tests all enforce the same truth claims

This is not a new image-processing capability project. It is a workflow-control, contract, and maintainability redesign for the existing package.

## Problem Statement

`split-image-assets` is already strong on package rigor:

- it has a concrete package contract
- it distinguishes structural validation from visual quality
- it records formal review state in metadata
- it has deterministic preview, audit, validation, and manifest tooling
- it has broad regression coverage

However, the current package still has three systemic problems.

### 1. Control-flow intent is still too easy to misuse

Future agents can still stop in the wrong place:

- to report progress
- because a stage is named a gate
- because confidence is imperfect
- because a question could be asked even though prior instructions already answer it

### 2. Extraction intent is still too extraction-centric

Text-like and rebuildable UI content can still be treated as raster-first unless the agent actively corrects for it. The package needs an explicit editability-first scoring and routing layer before extraction.

### 3. Contract implementation is too concentrated

The main validator, quality-review writer, and test suite have become large, concentrated contract hubs. The code works, but the maintenance surface is now too easy to drift:

- schema and taxonomy are duplicated across writer and validator
- multiple policy families are enforced in a few heavy modules
- tests rely on a single giant file and single giant class

This makes future contract changes expensive and increases the chance of green tests hiding local drift.

## User-Confirmed Requirements

The design is based on these explicit decisions from the current thread:

1. default to conservative continuous execution
2. only three hard event classes may pause execution
3. medium/high-risk semantic divergence may pause execution only by becoming a justified `user-decision` stop, not a fourth stop class
4. progress updates are commentary, not confirmation gates
5. the exit pattern should behave like `grill-me`: explain why a human is needed, recommend a path, and explain impact
6. asset splitting should be editability-first
7. ordinary text, button labels, numeric values, and form values should not become raster assets by default
8. logo wordmarks, decorative text, and fidelity-critical text may still become raster assets
9. ambiguous high-complexity text-like objects should route to `requires_user_confirmation`
10. when an object is not exported as an image asset, the package should still keep a text/object placeholder record for downstream or manual rebuild
11. development should be guided by a single total design document and a single aligned implementation plan

## Scope

In scope:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `docs/usage/split-image-assets.md`
- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/tests/test_skill_package.py`
- local architecture refactors required to reduce contract drift inside this package

Out of scope:

- changing segmentation or matting engines
- building OCR or full text understanding
- inventing a repo-wide shared interaction framework for unrelated skills
- adding new upstream model integrations as part of this redesign
- rewriting package semantics unrelated to stop/continue behavior, asset routing, or contract maintainability

## Non-Goals

This redesign should not:

- reduce the skill to a casual prompt
- turn every uncertainty into a stop
- allow `agent-defaulted` to satisfy real gates
- hide approximate assets inside production-ready claims
- export editable ordinary text as raster assets by default
- keep adding policy to monolithic modules without creating clearer ownership boundaries

## Design Principles

1. Continue by default.
2. Commentary is never control flow.
3. A semantic pause reason must map to a formal stop class.
4. Editability dominates unless fidelity clearly requires pixels.
5. Formal state must be durable, narrow, and auditable.
6. Contract rules should have a single code source where practical.
7. Tests should verify exact contract mappings, not just nearby wording.
8. Architecture should reduce drift risk, not merely pass current fixtures.

## Canonical Execution Contract

The package uses conservative continuous execution.

That means:

- the default state is `Running`
- the agent gathers evidence before escalating
- the workflow only exits when a human answer is required to preserve truth or claim level
- progress summaries remain commentary
- low-risk uncertainty stays inside execution

Every allowed exit must include:

- `Why This Needs a Human`
- `Recommendation`
- `Options and Impact`
- `What I Will Do After Confirmation`

## State Machine

The only execution states are:

- `Running`
- `AwaitingDecision`
- `AwaitingExternalBlocker`
- `AwaitingApproval`
- `Completed`

### `Running`

Use for:

- intake
- environment inspection
- recipe selection when already implied
- split planning
- asset value scoring
- import or packaging
- preview and audit generation
- metadata updates
- validation
- manifest export
- progress reporting

### `AwaitingDecision`

Use only when a real human choice is required and different answers materially change package semantics.

### `AwaitingExternalBlocker`

Use only when execution cannot honestly continue because tooling, upstream outputs, credentials, files, or another external prerequisite are missing.

### `AwaitingApproval`

Use only when evidence is sufficient and a formal approval changes claim level or revision state.

### `Completed`

Use only when the current run has reached a real terminal outcome.

## Stop Taxonomy

There are only three stop classes:

- `user-decision`
- `external-blocker`
- `formal-approval`

Medium/high-risk semantic divergence is not a fourth class. It is a trigger rule that may justify a `user-decision` stop when current evidence and prior instructions do not resolve the branch honestly.

## Gate Taxonomy

The following gates are the normalized execution taxonomy for this package.

| Gate | Stop class | State | Meaning |
| --- | --- | --- | --- |
| `tooling_preflight` | `external-blocker` | `AwaitingExternalBlocker` | choose or unblock a production-capable path |
| `granularity_alignment` | `user-decision` | `AwaitingDecision` | settle split scope and downstream rebuild boundaries |
| `pilot_object` | `formal-approval` | `AwaitingApproval` | approve widening a dense/high-risk batch |
| `approximate_reconstruction` | `user-decision` | `AwaitingDecision` | accept or reject an approximate visual truth claim |
| `final_acceptance` | `formal-approval` | `AwaitingApproval` | approve final package claim level |
| `candidate_promotion` | `formal-approval` | `AwaitingApproval` | replace the current owned revision |

### Gate Rules

#### `tooling_preflight`

- must stop only when no user-backed production path exists
- may continue when prior instructions already choose `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`

#### `granularity_alignment`

- must stop only when different split choices materially change reuse boundaries or rebuild expectations
- may continue when existing user intent already settles granularity, text handling, carrier/glyph policy, background expectation, and layer independence

#### `pilot_object`

- must stop only when widening the batch without approval would materially increase cleanup cost or semantic drift
- may continue with `not-required` only when supported by prior instructions or clear recorded policy

#### `approximate_reconstruction`

- must stop only when accepting approximation changes truthfulness or downstream use
- may continue without stopping when prior instructions already allow approximation and the asset remains explicitly approximate
- this gate is a `user-decision`, not a `formal-approval`

#### `final_acceptance`

- must stop only when the package is otherwise ready and a pass claim still needs formal acceptance
- must not be used just to announce completion

#### `candidate_promotion`

- must stop only when the current revision is about to change without an already approved policy covering that promotion
- must not silently promote a staged candidate

## Asset Value Scoring Contract

Asset value scoring runs before extraction.

The question is not “can this be extracted?” The question is “should this object exist as a raster asset at all?”

### Scoring Axes

Each object may carry:

- `value_scoring.editability_score`
- `value_scoring.visual_complexity_score`
- `value_scoring.asset_value_score`
- `value_scoring.scoring_reason`

### Text-Like Classification

Each object may carry:

- `text_semantics.text_role`
- `text_semantics.text_render_class`

Allowed `text_role` values:

- `plain-text`
- `button-label`
- `numeric-value`
- `form-value`
- `logo-wordmark`
- `decorative-text`
- `non-text`

Allowed `text_render_class` values:

- `editable`
- `styled-editable`
- `visual-fidelity-critical`
- `non-text`

### Routing Outcomes

Each object must resolve to one of:

- `extract_asset`
- `rebuild_downstream`
- `requires_user_confirmation`
- `support_only`

### Routing Rules

- ordinary text, button labels, numeric values, and form values default to `rebuild_downstream`
- logo wordmarks, decorative text, and fidelity-critical text may default to `extract_asset`
- ambiguous high-complexity text-like objects route to `requires_user_confirmation`
- `requires_user_confirmation` is a `user-decision` stop only when ambiguity is real and unresolved
- `rebuild_downstream` objects do not export a production raster asset, but they still keep a placeholder/object record in metadata

## Formal State Surfaces

`metadata.decision_log[]` and `metadata.confirmation` are formal-state surfaces.

They exist to record:

- real gate decisions
- real approval outcomes
- real evidence-backed inferred user intent

They must not contain:

- progress updates
- routine commentary
- stage-complete notes
- “still working” status
- agent guesswork

Object-specific semantic divergence must stay object-scoped in evidence and confirmation effects. One object's accepted path must not implicitly satisfy another object's branch.

## Truthfulness Rules

- `qa.status=pass` requires a production-capable path, valid final acceptance, and passing required checks
- approximate or reconstructed layers must remain explicitly approximate
- `delivery_class=approximate-reconstruction` must stay visible when approximation is involved
- approximate layers must not be reported as `production-ready`
- draft-only runs must remain draft-honest

## Architecture Requirements

The next implementation phase should not keep piling contract logic into the existing hotspots. The design requires the following code-shape changes.

### 1. Shared Contract Source

Move shared enums, gate mappings, confirmation defaults, and other repeated taxonomy data into a single package-local contract module consumed by:

- `record_quality_review.py`
- `validate_asset_package.py`
- tests that check exact mappings

### 2. Validator Decomposition

Split validator responsibilities into package-local domains, at minimum:

- metadata contract validation
- object routing and asset-policy validation
- preview and filesystem validation
- candidate comparison and promotion evidence validation

### 3. Review Writer Decomposition

Separate:

- CLI argument parsing
- metadata mutation helpers
- confirmation/decision writing
- object routing updates
- QA report append logic

### 4. Test Decomposition

Break the giant package test file into domain-focused modules over time:

- docs and contract wording
- package init and write-path behavior
- validator contract enforcement
- candidate workflow behavior
- end-to-end acceptance flows

This does not need to be one big-bang rewrite, but the target architecture should be clear before adding more policy.

## Success Criteria

The redesign is successful when all of the following are true:

1. there is one canonical design doc and one canonical implementation plan
2. package docs all express the same stop/continue contract
3. asset routing is editability-first and auditable
4. `approximate_reconstruction` is treated consistently as a `user-decision` gate
5. writer and validator no longer own conflicting copies of the same contract data
6. tests fail on exact contract drift, not only broad wording drift
7. future work can be phased without reopening design intent
