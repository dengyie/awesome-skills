# Split Image Assets Unified Agent-First Design

Date: 2026-06-30
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

This redesign now also includes a fourth property:

4. installation and runtime setup should default to an isolated, container-first path that maps cleanly into the same capability model used by the workflow itself

This is not a new image-processing capability project. It is a workflow-control, contract, and maintainability redesign for the existing package.

## Problem Statement

`split-image-assets` is already strong on package rigor:

- it has a concrete package contract
- it distinguishes structural validation from visual quality
- it records formal review state in metadata
- it has deterministic preview, audit, validation, and manifest tooling
- it has broad regression coverage

However, the current package still has four systemic problems.

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

### 4. Installation experience is still too raw and environment-coupled

The package currently knows how to detect missing upstream capability, but not how to give users a clean, low-risk path to obtain that capability.

Current failure modes:

- users are shown missing-package lists instead of a clear install path
- the package does not distinguish installer UX from runtime preflight clearly enough
- there is no canonical `draft` versus `recommended` versus `production` installation story
- users can easily pollute their host Python while trying to satisfy recommended tooling
- platform-specific reality such as Apple Silicon, Linux CUDA, Docker compatibility, or fallback paths is not surfaced as a first-class design concern

The result is that the package is strong at honesty after setup, but weak at helping a user reach a good setup safely.

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
12. installation should avoid polluting the user's environment whenever practical
13. the default installation path should be container-first
14. the runtime abstraction should be Docker-compatible rather than Docker-only
15. the default installation target should be `recommended`, not merely the weakest runnable draft path
16. `mac-apple-silicon` should be the primary supported path, with `linux-cuda` as the secondary path

## Scope

This section defines the active scope for the current installer UX line, not the full historical scope of every earlier `split-image-assets` refactor.

In scope for the current active line:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/pipeline-recipes.md`
- `docs/usage/split-image-assets.md`
- `split-image-assets/scripts/check_extraction_environment.py`
- new package-local capability helpers
- new package-local installer and verification entrypoints
- `split-image-assets/tests/test_skill_package.py`
- docs/tests/runtime wording changes required to keep installer UX and preflight language aligned

Conditionally in scope only if installer UX work exposes drift that must be corrected for honesty:

- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`

Out of scope:

- changing segmentation or matting engines
- building OCR or full text understanding
- inventing a repo-wide shared interaction framework for unrelated skills
- adding new upstream model integrations as part of this redesign
- rewriting package semantics unrelated to stop/continue behavior, asset routing, or contract maintainability
- building a general-purpose environment manager for unrelated skills

## Active-Line Disposition

The earlier contract-hardening line remains part of the package baseline, but it is not the active milestone now.

Its status for the purpose of this document is:

- canonical stop taxonomy, asset-routing semantics, and validator/writer truth rules remain required baseline constraints
- installer UX work must preserve those constraints
- unfinished or future contract-hardening cleanups are backlog unless they become direct blockers for the current installer UX milestone

This means the current active line is installer UX V1, while the earlier contract-hardening work is treated as preserved baseline plus backlog, not as a parallel active milestone.

## Non-Goals

This redesign should not:

- reduce the skill to a casual prompt
- turn every uncertainty into a stop
- allow `agent-defaulted` to satisfy real gates
- hide approximate assets inside production-ready claims
- export editable ordinary text as raster assets by default
- keep adding policy to monolithic modules without creating clearer ownership boundaries
- default to installing recommended tooling directly into the user's host Python when an isolated path is available
- pretend that package import success alone proves runtime or production readiness

## Design Principles

1. Continue by default.
2. Commentary is never control flow.
3. A semantic pause reason must map to a formal stop class.
4. Editability dominates unless fidelity clearly requires pixels.
5. Formal state must be durable, narrow, and auditable.
6. Contract rules should have a single code source where practical.
7. Tests should verify exact contract mappings, not just nearby wording.
8. Architecture should reduce drift risk, not merely pass current fixtures.
9. Installation should be isolated by default.
10. Installer output should be action-first rather than dependency-list-first.

## Installer UX Architecture

Installation is part of the package contract, not just a README appendix.

The installer UX should answer four user questions quickly:

1. what profile am I on
2. what capability tier do I have now
3. what is the recommended safe install path
4. what command should I run next

### Core Principles

#### `container-first`

The default installation path should prefer an isolated runtime over host-environment mutation.

That means:

- prefer containerized setup when a compatible container runtime exists
- treat host-`venv` as a fallback, not the main product path
- never assume that modifying the user's global Python is acceptable

#### `docker-compatible`

The design should target a Docker-compatible runtime contract rather than a single vendor implementation.

Valid container runtime paths may include:

- `docker`
- `podman`
- `colima` plus Docker-compatible CLI behavior

The design should express runtime capability as a compatibility class, not a branding choice.

#### `recommended-by-default`

The default installation target should be `recommended`.

The package still supports:

- `draft`
- `recommended`
- `production`

But the default story should not stop at “lowest possible success.” It should optimize for the best capability-to-friction tradeoff for typical users.

#### Shared capability language

Installer UX, verification, runtime preflight, and docs must all use the same vocabulary for:

- profiles
- presets
- runtime mode
- readiness tiers
- missing components
- next-step recommendations

The package should not let `doctor`, `install`, `verify`, and runtime preflight each invent separate language for the same environment state.

#### Action-first output

Installer-related commands must lead with:

- the conclusion
- the current tier
- the recommended next command

They must not force the user to infer next steps from a long missing-package list.

### Runtime Modes

The package supports two runtime modes:

- `container`
- `venv`

Default routing rules:

- use `container` when a Docker-compatible runtime is available
- recommend `venv` only when container mode is unavailable or explicitly declined

### Platform Profiles

The installer UX must reason in named profiles.

Primary profile:

- `mac-apple-silicon`

Secondary profile:

- `linux-cuda`

These profiles are not just labels for docs. They should affect:

- recommended preset resolution
- runtime recommendations
- dependency hints
- verification expectations

### Capability Presets

The installer UX must reason in named presets.

#### `draft`

Purpose:

- package structure, import, preview, QA, and validation
- external-professional-output workflows

This preset does not promise mature local segmentation, matting, or reconstruction.

#### `recommended`

Purpose:

- best default value path for most users
- local segmentation workflow with mature enough capability to be useful without requiring the heaviest possible stack discipline

This is the default preset.

#### `production`

Purpose:

- closest path to the package's `production-capable` claim
- stricter runtime and role-readiness requirements

This preset is not defined merely by more installed packages. It is defined by verified component readiness across the required upstream roles.

### Default Resolution

If the user does not specify a mode, profile, or preset:

- detect the profile
- prefer `container`
- default to `recommended`

Typical resolved targets:

- `mac-apple-silicon + container + recommended`
- `linux-cuda + container + recommended`

### Command Surface

The installer UX should expose four primary entrypoints:

- `doctor`
- `install`
- `verify`
- `explain`

#### `doctor`

Responsibilities:

- detect platform profile
- detect runtime mode availability
- evaluate Python and environment suitability
- report current capability tier
- report what is missing for `recommended` and `production`
- provide a single recommended next command

`doctor` should not mutate the environment.

#### `install`

Responsibilities:

- resolve or accept explicit profile, preset, and runtime mode
- create isolated setup artifacts for the chosen path
- install or prepare components in a staged, explainable sequence
- record what was installed, skipped, failed, or deferred to manual/container runtime setup
- invoke `verify` at the end

`install` should prioritize container mode first and only recommend `venv` fallback when container mode is not available or not desired.

#### `verify`

Responsibilities:

- re-evaluate the environment after installation
- confirm import readiness and runtime readiness
- classify the resulting tier honestly
- describe what the user can do now
- describe what still blocks `production`

`verify` must enforce the distinction between:

- `installed`
- `runtime_ready`
- `production_ready`

#### `explain`

Responsibilities:

- explain why a preset or runtime mode is recommended
- explain why a current environment is not `production`
- explain component roles such as why `rembg` is fallback-only or why dedicated reconstruction still matters

This keeps explanation out of the main install path while still making the system understandable.

### Shared Capability Model

The package should use one shared capability model across installer UX and runtime preflight.

At minimum it should encode:

- runtime mode availability
- container runtime availability details
- profile detection
- preset target
- component states
- upstream role readiness
- capability tier

Each component should support at least:

- `installed`
- `runtime_ready`
- `production_ready`

The design must state clearly:

- installation success does not guarantee runtime readiness
- runtime readiness does not guarantee production readiness

This distinction is especially important for:

- `torch`
- `SAM2`
- `GroundingDINO`
- matting tools
- dedicated reconstruction tools

### Relationship To Runtime Preflight

Runtime preflight should no longer act as the primary installation UX.

Instead:

- installer UX becomes the primary entry surface for setup
- runtime preflight becomes a runtime truth-check and routing surface
- when preflight finds missing capability, it should route users toward `doctor`, `install`, or `verify` instead of only listing raw missing tools

The runtime preflight should still remain authoritative for claim-level honesty, but it should no longer carry the full burden of teaching users how to reach a good environment.

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
