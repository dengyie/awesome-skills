# Split Image Assets Interaction Framework Design

Date: 2026-06-28
Status: Proposed and user-approved for spec drafting
Target package: `split-image-assets`

## Goal

Refactor `split-image-assets` into a unified interaction framework where execution only pauses for legitimate user decisions, genuine external blockers, or formal approval gates, while ordinary progress reporting always stays in commentary and never blocks execution.

## Problem Statement

`split-image-assets` already contains strong workflow gates, confirmation prompts, metadata contracts, validator rules, and package tests. However, its interaction control is still distributed across multiple layers:

- `SKILL.md` describes confirmation-driven behavior
- `references/workflow.md` defines staged gate sequencing
- `references/confirmation-prompts.md` provides one-question prompt templates
- `references/asset-package-contract.md` defines metadata fields
- `scripts/record_quality_review.py` writes gate state into metadata
- `scripts/validate_asset_package.py` enforces part of the package contract
- `tests/test_skill_package.py` verifies selected gate and validation behavior

This distribution creates three practical risks:

1. progress updates can still be mistaken for reasons to stop and wait
2. formal gates can still be represented too loosely in metadata
3. agent-authored defaults can still leak into decision/confirmation state instead of forcing a real user-backed decision

The desired behavior is stricter:

1. only three event classes may pause execution
2. progress updates are commentary only
3. formal gates must never be satisfied by `agent-defaulted`
4. `inferred-from-user` must mean evidence-backed user intent, not agent guesswork
5. tooling, metadata, validation, and tests must all enforce the same interaction rules

## Scope

This refactor applies only to the local `split-image-assets` package and its package-level usage guide.

In scope:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/tests/test_skill_package.py`
- `docs/usage/split-image-assets.md`

Out of scope:

- editing upstream `superpowers:brainstorming`
- adding a repository-wide shared interaction library used by multiple skills
- changing unrelated split-image asset extraction logic, image processing logic, or package layout beyond what is necessary for the interaction contract
- adding a migration helper for historical metadata in this phase

## Non-Goals

This refactor should not:

- rewrite the extraction workflow itself
- replace existing confirmation prompts with a multi-question survey style
- add broad new asset classes or quality tiers
- silently auto-migrate old metadata and treat it as fully compliant
- create a generic framework package shared across the whole repo in this phase

## Design Principles

The interaction framework should follow these principles:

1. commentary is not control flow
2. pause decisions must be explicit and classifiable
3. every formal gate must have a durable metadata trace
4. inferred decisions must point to real user evidence
5. validation should enforce interaction truth, not only field presence
6. tests should fail when old ambiguous pause behavior reappears

## Pause State Machine

`split-image-assets` should standardize on the following execution states:

- `Running`
- `AwaitingDecision`
- `AwaitingExternalBlocker`
- `AwaitingApproval`
- `Completed`

### State Meanings

`Running`

- the workflow is actively analyzing, importing, generating previews, scoring candidates, auditing quality, validating structure, or recording evidence
- commentary updates are allowed
- commentary must not pause execution

`AwaitingDecision`

- the workflow reached a real user decision point that affects reuse boundaries, tool path, granularity, text handling, reconstruction acceptance, or other material package semantics
- exactly one focused question should be asked
- a recommended answer should be included

`AwaitingExternalBlocker`

- the workflow cannot proceed because it lacks permissions, professional upstream outputs, required installs/activation, credentials, devices, or other external prerequisites
- the blocker must be described concretely
- this state must not be used for ordinary uncertainty

`AwaitingApproval`

- the workflow has enough evidence to ask for a formal approval decision before broadening execution or escalating claims
- examples include pilot approval, final acceptance, or candidate promotion approval

`Completed`

- the workflow reached a real terminal outcome for the current run
- terminal outcomes must not be implied by progress commentary

### Interaction Iron Rules

The refactor should codify these rules in `SKILL.md` and supporting references:

```text
PROGRESS UPDATES ARE COMMENTARY, NOT CONFIRMATION GATES
ONLY THREE EVENT TYPES MAY PAUSE EXECUTION
NO FORMAL GATE MAY BE SATISFIED BY AGENT DEFAULTING
INFERRED-FROM-USER MEANS EVIDENCE-BACKED USER INTENT, NOT AGENT GUESSING
```

## Gate Taxonomy

Every formal gate should be mapped to one of the three allowed pause categories.

### Gate Classes

Allowed pause categories:

- `user-decision`
- `external-blocker`
- `formal-approval`

### `tooling_preflight`

Classification:

- primarily `external-blocker`
- may also become `user-decision` when the environment supports multiple user-selectable paths

Pause state:

- `AwaitingExternalBlocker` when required capability is missing
- `AwaitingDecision` when the user must choose among valid paths

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user`

Illegal source:

- `agent-defaulted`

Must pause when:

- no user-backed choice exists for `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`

May continue without pausing when:

- existing user instructions, package metadata, or previously approved policy already select the path for the current run

### `granularity_alignment`

Classification:

- `user-decision`

Pause state:

- `AwaitingDecision`

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user`

Illegal source:

- `agent-defaulted`

Must pause when:

- split scope is still ambiguous and different answers would materially change asset boundaries, text handling, carrier/glyph behavior, background expectations, or layer independence

May continue without pausing when:

- the existing user brief, confirmed metadata, or approved design already resolves the current granularity branch

### `pilot_object`

Classification:

- `formal-approval`

Pause state:

- `AwaitingApproval`

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user` only for evidence-backed `not-required`

Illegal source:

- `agent-defaulted`

Must pause when:

- a dense UI or approximate reconstruction workflow requires pilot approval before wider batch expansion and no valid prior approval exists

May continue without pausing when:

- approved prior evidence clearly marks pilot as `not-required` for the current run or object class

### `approximate_reconstruction`

Classification:

- first `user-decision`
- later `formal-approval` when claim escalation is at stake

Pause state:

- `AwaitingDecision` for acceptability of approximation
- `AwaitingApproval` when approximation affects final claim escalation

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user`

Illegal source:

- `agent-defaulted`

Must pause when:

- approximation changes truthfulness of deliverables and no existing approved acceptance policy covers the layer

May continue without pausing when:

- the user already explicitly accepted approximate reconstruction for the relevant layer class and usage target

### `final_acceptance`

Classification:

- `formal-approval`

Pause state:

- `AwaitingApproval`

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user` only when previously approved evidence already covers the current acceptance claim

Illegal source:

- `agent-defaulted`

Must pause when:

- the workflow is about to upgrade the package or object into `qa.status=pass`, `visual-acceptance-ready`, or `production-ready` without prior acceptance evidence

May continue without pausing when:

- the package is simply replaying validation against a previously approved unchanged acceptance baseline

### `candidate_promotion`

Classification:

- `formal-approval`

Pause state:

- `AwaitingApproval`

Allowed sources:

- `explicit-user-confirmed`
- `inferred-from-user` only when a prior approved policy clearly authorizes promotion under the current compare or direct-promotion conditions

Illegal source:

- `agent-defaulted`

Must pause when:

- a candidate asset is about to replace the current revision and no approved promotion rule covers the replacement

May continue without pausing when:

- a valid prior user-backed promotion rule already covers the specific object class and promotion path

## Metadata Contract Changes

### `decision_log`

`decision_log[]` should be repurposed as a strict formal-gate decision log, not a general progress or note log.

Required fields for each entry:

- `stage`
- `pause_category`
- `question`
- `recommended_answer`
- `recorded_answer`
- `decision_effect`
- `decision_source`
- `evidence_ref`
- `blocking`

Rules:

- `decision_source` may only be `explicit-user-confirmed` or `inferred-from-user`
- `agent-defaulted` is not legal in formal gate decision entries
- `inferred-from-user` requires a non-empty `evidence_ref`
- `blocking` records whether this gate actually blocked downstream execution
- `recorded_answer` replaces the old `user_answer` because inferred answers may be mapped from existing user evidence rather than newly typed in the current turn

### `confirmation`

`confirmation` should remain the lightweight gate-state registry, but it must adopt the same source rigor.

Required keys:

- `tooling_preflight`
- `granularity_alignment`
- `pilot_object`
- `approximate_reconstruction`
- `final_acceptance`
- `candidate_promotion`

Each confirmation entry should include:

- `status`
- `source`
- `pause_category`
- `notes`
- `evidence_ref`

`pilot_object` must also include:

- `object_id`

Rules:

- `status=confirmed` or `status=not-required` may only use `explicit-user-confirmed` or `inferred-from-user`
- `status=pending` may use `unset`
- `not-required` must mean evidence-backed non-applicability, not agent convenience

### Commentary Separation

Progress summaries, tool output notes, and audit commentary must not be stored in `decision_log` or `confirmation`. They may still be written into ordinary QA or review note surfaces, but they cannot count as gate evidence.

## Script Contract

### `record_quality_review.py`

The script should split writes into two modes:

1. `formal gate write`
2. `commentary / review note write`

Formal gate writes are triggered by:

- `--decision-stage`
- `--confirmation-key`
- any decision stage mapped to a hard confirmation key

For formal gate writes:

- `--decision-source` or `--confirmation-source` must be required
- `agent-defaulted` must be rejected
- `--pause-category` must be required
- `--blocking` must be required for decision-log writes
- `--evidence-ref` must be required when source is `inferred-from-user`

Commentary writes:

- may continue to append review notes or non-gate evidence
- must not create or mutate formal confirmation state
- must not create decision-log entries

Recommended helper responsibilities:

- detect whether a stage is a formal gate
- enforce legal formal gate sources
- require evidence for inferred decisions
- normalize pause category values

### `validate_asset_package.py`

The validator must enforce interaction legality, not just field completeness.

New or tightened checks:

- formal decision entries must not use `agent-defaulted`
- formal confirmation entries with `confirmed` or `not-required` must not use `agent-defaulted`
- `inferred-from-user` requires `evidence_ref`
- `pause_category` must be one of the three allowed values
- blocking gates must be cleared before downstream claim escalation
- `candidate_promotion` must be present and valid when promoted revision state exists
- progress commentary must not masquerade as gate metadata

Flow-consistency checks:

- `qa.status=pass` requires confirmed `tooling_preflight`, `granularity_alignment`, and `final_acceptance`
- packages with approximate reconstructed layers must clear `approximate_reconstruction` before claim escalation
- dense UI or similar packages that depend on a pilot strategy must clear `pilot_object` before widened batch approval paths
- promoted candidate assets must have matching candidate-promotion clearance

## File-by-File Refactor Plan

### `split-image-assets/SKILL.md`

Add:

- the unified interaction iron rules
- the pause state machine summary
- explicit gate type / allowed source / pause category statements
- commentary vs confirmation-gate separation
- `candidate_promotion` as a first-class approval gate

Do not add:

- low-level CLI syntax
- migration procedures

### `split-image-assets/references/workflow.md`

Add:

- state-machine semantics at the top
- explicit pause category and blocking notes for every gate
- strict gate ordering constraints
- clear prevention of “ask when needed” ambiguity

### `split-image-assets/references/confirmation-prompts.md`

Add:

- pause category annotation per prompt
- explicit must-ask vs may-infer guidance per prompt
- a section explaining what is not a confirmation prompt

### `split-image-assets/references/asset-package-contract.md`

Change:

- formalize the new `decision_log` and `confirmation` schemas
- remove `agent-defaulted` from formal legal source values
- define evidence-backed inference rules
- document commentary separation

### `split-image-assets/scripts/record_quality_review.py`

Change:

- remove default `agent-defaulted` for formal gate writes
- require source, pause category, and blocking metadata for formal gate decisions
- require evidence for inferred decisions
- keep commentary writes separate from gate writes

### `split-image-assets/scripts/validate_asset_package.py`

Change:

- reject illegal formal source values
- reject inferred decisions without evidence
- validate blocking-flow consistency
- validate candidate promotion clearance

### `split-image-assets/tests/test_skill_package.py`

Add:

- contract wording tests for the new interaction framework
- script behavior tests for missing source, illegal source, and missing evidence
- validator tests for blocking gates, promotion approval, commentary/gate separation, and inferred-evidence enforcement

### `docs/usage/split-image-assets.md`

Add:

- a user-facing section explaining when the skill pauses
- a user-facing explanation that progress updates do not interrupt execution

## Implementation Phases

### Phase 1: Interaction Contract Unification

Files:

- `SKILL.md`
- `references/workflow.md`
- `references/confirmation-prompts.md`

Done when:

- the unified pause-state rules are documented clearly and consistently

### Phase 2: Metadata Contract Hardening

Files:

- `references/asset-package-contract.md`

Done when:

- metadata schemas express formal gate legality directly

### Phase 3: Script Write-Path Refactor

Files:

- `scripts/record_quality_review.py`

Done when:

- invalid formal gate states can no longer be created through the script

### Phase 4: Validator Enforcement Upgrade

Files:

- `scripts/validate_asset_package.py`

Done when:

- illegal gate/source/evidence combinations are rejected

### Phase 5: Regression Test Expansion

Files:

- `tests/test_skill_package.py`

Done when:

- old ambiguous interaction behavior reliably fails tests

### Phase 6: User-Facing Documentation Sync

Files:

- `docs/usage/split-image-assets.md`

Done when:

- external users can predict the skill’s pause behavior without reading internal references

## Acceptance Criteria

The refactor is complete only when all of the following are true:

1. only three event classes may pause execution
2. progress updates are commentary, not confirmation gates
3. formal gate metadata never accepts `agent-defaulted`
4. `inferred-from-user` always requires evidence
5. `candidate_promotion` is treated as a formal gate across docs, metadata, validator, and tests
6. `record_quality_review.py` cannot write illegal formal gate state
7. `validate_asset_package.py` rejects illegal interaction-state combinations
8. package tests catch regressions back to ambiguous pause behavior

## Test Strategy

Minimum new regression themes:

- progress commentary does not create gate state
- formal gate writes reject missing or illegal source
- inferred decisions require evidence
- candidate promotion requires gate clearance
- blocking gates prevent downstream claim escalation

## Compatibility Strategy

This phase should not silently normalize historical metadata into compliance.

Policy:

- new writes must follow the new contract
- old metadata may be read
- validator should fail clearly on old illegal gate-source patterns
- migration tooling, if needed later, should be a separate phase

## Review Checklist

Before implementation planning begins, verify that:

1. no section still allows progress-based pauses
2. no formal gate can be cleared without explicit or evidence-backed user sourcing
3. inferred decisions are always tied to durable evidence
4. promotion and pass-claim paths cannot bypass approval gates
5. commentary and gate state are cleanly separated across docs and tools
6. the refactor stays scoped to `split-image-assets`
