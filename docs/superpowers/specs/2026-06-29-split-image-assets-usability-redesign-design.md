# Split Image Assets Usability Redesign Design

Date: 2026-06-29
Status: Proposed and user-approved for spec drafting
Target package: `split-image-assets`

## Goal

Refactor `split-image-assets` into an agent-first usability model that defaults to continuous execution, exits only for legitimate human-required confirmation points, and presents those exits in a `grill-me` style with a clear recommendation and explicit impact.

## Primary Outcome

The main outcome of this redesign is not a new extraction capability. The main outcome is a stricter execution contract:

1. the default state is `Running`
2. progress reports stay in commentary and do not pause execution
3. the skill may only stop for hard gate events or medium/high-risk semantic divergence
4. every stop must explain why a human is needed now, what the recommendation is, and what each option changes
5. workflow docs, skill docs, metadata contracts, and tests all describe the same stop/continue behavior

## Problem Statement

`split-image-assets` is already strong on packaging rigor:

- it has a real package contract
- it distinguishes structural validation from visual quality
- it has deterministic scripts for previews, audit, validation, and manifest export
- it records formal review state in metadata
- it has broad package tests

However, its execution usability for agents is still too easy to misuse.

The main failure mode is not “the agent cannot do the work.” The main failure mode is “the agent stops in the wrong place.”

Today, a future agent can still misread the workflow as:

- pause to report stage completion
- pause because confidence is imperfect
- pause because a workflow step contains the word “gate”
- pause because a question could be asked, even though prior instructions already answer it
- pause because a local warning exists, even though the workflow can continue and record evidence first

That produces four practical usability failures:

1. continuous work is broken by unnecessary confirmation requests
2. users are asked to approve progress instead of decisions
3. future agents lose the distinction between commentary, decision points, blockers, and approvals
4. the skill's formal interaction contract becomes weaker than its package contract

This redesign treats that as a first-class usability bug.

## User-Approved Requirements

The design is based on these confirmed decisions:

1. this is a full usability redesign, not a narrow patch
2. the primary audience is the executing agent, not the casual human reader
3. the top priority failure mode is “stopping in the wrong place”
4. the desired execution style is conservative continuous execution
5. the skill should only exit the workflow when human confirmation is genuinely required
6. the exit pattern should behave like `grill-me`: explain the issue, provide a recommendation, and explain impact
7. allowed proactive exit events are:
   - the three hard event classes
   - medium/high-risk semantic divergence
8. low-risk uncertainty, progress updates, and recoverable workflow ambiguity should not stop execution
9. the deliverable should be a single total design document that later development can execute directly

## Scope

This redesign applies to the local `split-image-assets` package and its usage documentation.

In scope:

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `docs/usage/split-image-assets.md`
- package tests that enforce interaction behavior
- small deterministic script/documentation adjustments required to keep the interaction contract internally coherent

Out of scope:

- changing the upstream segmentation or matting engines
- adding new extraction model integrations
- redesigning the asset package schema beyond what is needed for interaction clarity
- replacing the QA/audit/validation toolchain
- building a repo-wide shared interaction framework used by unrelated skills
- turning this phase into a generic “make the skill easier for humans” rewrite

## Non-Goals

This redesign should not:

- reduce the skill to a lightweight casual prompt
- remove formal approval gates
- allow agents to satisfy real decisions through `agent-defaulted`
- ask the user about every low-confidence branch
- create stage-checkpoint pauses with no real human choice
- weaken the production/draft/approximate truthfulness rules

## Target Persona

The target persona is:

- an agent with access to the local skill files and scripts
- moderate code execution ability
- weak judgment about when to stop versus when to continue
- a tendency to confuse “worth mentioning” with “must ask”

The design should optimize for that agent, not for an expert maintainer who already knows the intended workflow.

## Usability Diagnosis

From an agent-first usability perspective, `split-image-assets` is already strong in correctness but weaker in control-flow clarity.

Current strengths:

- package outputs are structured and auditable
- quality and validation boundaries are explicit
- script boundaries are unusually honest
- text-like asset routing now reflects realistic downstream rebuild logic

Current usability weaknesses:

1. the workflow still presents too many “gates” without a sufficiently strict pause policy
2. the docs are rich but not yet shaped around the default question “should I continue or should I stop?”
3. the agent has to infer too much from prose instead of reading a compact event taxonomy
4. entry guidance is still more contract-heavy than execution-heavy

This redesign addresses those weaknesses without relaxing the package contract.

## Design Principles

The redesign should follow these principles:

1. default to continued execution
2. commentary is never control flow
3. stopping is exceptional, classifiable, and auditable
4. every stop must be worth the user's interruption
5. if prior instructions already resolve a branch, record them and continue
6. medium/high-risk semantic divergence is the only non-hard-event reason to stop
7. the same policy must appear consistently in skill docs, workflow docs, and tests

## Default Execution Model

`split-image-assets` should adopt **conservative continuous execution**.

That means:

- the agent continues by default
- the agent records evidence before escalating uncertainty
- the agent only exits the workflow when a human answer is required to preserve deliverable truth
- “I should probably mention this” becomes commentary
- “I cannot choose this branch honestly without a human” becomes a stop

This is intentionally stricter than a generic low-confidence pause model.

## Execution State Machine

The package should standardize on these states:

- `Running`
- `AwaitingDecision`
- `AwaitingExternalBlocker`
- `AwaitingApproval`
- `Completed`

### `Running`

Use `Running` for:

- source intake
- package initialization
- preflight inspection and capability reporting
- recipe selection when already implied by prior instructions
- split planning
- asset value scoring
- import and packaging
- preview generation
- audit generation
- metadata recording
- validation
- manifest export
- warning collection
- progress updates

`Running` is the default state.

### `AwaitingDecision`

Use `AwaitingDecision` only when a real user choice is required and different answers materially change package semantics.

Examples:

- rebuild downstream versus keep as visual asset
- split carrier and glyph versus keep grouped
- allow approximate reconstruction versus require exact extraction
- choose one of multiple valid workflow paths when the choice is not already resolved

### `AwaitingExternalBlocker`

Use `AwaitingExternalBlocker` only when execution cannot honestly continue due to a real external dependency.

Examples:

- required professional capability is missing
- expected upstream outputs are unavailable
- required install/activation path is missing
- required credentials, files, or permissions are unavailable

### `AwaitingApproval`

Use `AwaitingApproval` when the work is ready for a formal approval gate that changes claim level or promotion state.

Examples:

- pilot approval before wider UI batch
- final acceptance before `qa.status=pass`
- candidate promotion before replacing the current revision

### `Completed`

Use `Completed` only when the current run has reached a real terminal outcome such as:

- structurally valid package produced
- package blocked for explicit external reasons
- package finalized after approval

Progress updates never imply `Completed`.

## Event Taxonomy

The redesign introduces a strict two-layer taxonomy.

### Layer 1: Hard Stop Events

These are always allowed to stop execution:

- `user-decision`
- `external-blocker`
- `formal-approval`

### Layer 2: Semantic Divergence Events

These may stop execution only when they are medium or high risk.

Definition:

- the agent has identified two or more materially different semantic interpretations
- the difference changes downstream truth, reuse value, or promotion claim
- the workflow cannot honestly choose one branch from current evidence and prior instructions

Allowed examples:

- text-like region should be rebuilt downstream or preserved as a visual asset
- carrier/glyph should split or stay grouped
- approximate reconstruction is acceptable or not
- granularity branch changes whether the package is atomic-layer or production-editable in a material way

Disallowed examples:

- local visual warning that can still be audited and recorded
- a likely but non-material split preference
- uncertainty that can be resolved by continuing preview/audit/validation work
- stage completion summaries
- “I want to make sure” pauses with no real semantic branch

## Stop Eligibility Rules

A proactive workflow exit is allowed only when all of the following are true:

1. the event matches a hard stop class or medium/high-risk semantic divergence
2. the answer is not already settled by prior user instructions or durable metadata
3. continuing without a human answer would risk a false claim, wrong semantic asset boundary, or wrong delivery path
4. the stop can be expressed as one focused question with a recommendation

If any one of those conditions is false, the workflow should continue in commentary.

## Grill-Me Style Exit Contract

Every allowed stop must use the same interaction shape.

Required sections:

1. `Why This Needs a Human`
2. `Recommendation`
3. `Options and Impact`
4. `What I Will Do After Confirmation`

### Contract Requirements

`Why This Needs a Human`

- explain the exact branch that is unresolved
- explain why the branch is semantic, external, or approval-critical
- do not use generic language like “just checking”

`Recommendation`

- provide one recommended answer
- explain why it is the best default from current evidence

`Options and Impact`

- present the real alternatives
- explain how each answer changes the package or claim

`What I Will Do After Confirmation`

- say what the workflow will do next after the answer
- this keeps the stop attached to the continuing execution path

### Anti-Patterns

These must be explicitly forbidden:

- “please confirm before I continue” with no recommendation
- progress-only pauses
- multiple unrelated questions in one stop
- asking for confirmation when prior instructions already answer the branch
- pausing because a workflow stage ended

## Gate Taxonomy Mapping

This redesign keeps the existing gate concepts but reclassifies how they behave.

### `tooling_preflight`

Default mode:

- `Running`

Pause only when:

- the workflow cannot honestly continue without the user's choice among `install-or-activate-tools`, `external-professional-outputs`, or `draft-packaging-only`
- or a real external capability blocker prevents the requested quality target

State mapping:

- `AwaitingExternalBlocker` for true missing capability
- `AwaitingDecision` when multiple valid user-selectable paths exist and prior instructions do not already resolve them

Not a valid stop reason:

- reporting the capability matrix itself

### `granularity_alignment`

Default mode:

- `Running`

Pause only when:

- the chosen granularity materially changes downstream semantics and is not already implied by the brief

State mapping:

- `AwaitingDecision`

Not a valid stop reason:

- merely recording the granularity axes

### `pilot_object`

Default mode:

- `Running`

Pause only when:

- the current UI/dense-composition workflow truly needs a pilot approval before scaling up and there is no prior evidence-backed `not-required`

State mapping:

- `AwaitingApproval`

Important change:

- pilot is no longer treated as a default stage checkpoint

### `approximate_reconstruction`

Default mode:

- `Running` while collecting evidence

Pause only when:

- the acceptability of approximation is a medium/high-risk semantic divergence
- or a higher claim is about to be made from approximate output

State mapping:

- `AwaitingDecision` for acceptability
- `AwaitingApproval` for final claim escalation

### `final_acceptance`

Default mode:

- not entered until the package is actually ready

Pause when:

- the workflow is about to claim `qa.status=pass` or equivalent final acceptance

State mapping:

- `AwaitingApproval`

### `candidate_promotion`

Default mode:

- `Running` while gathering compare evidence

Pause when:

- one candidate is about to replace the current revision

State mapping:

- `AwaitingApproval`

## Documentation Information Architecture

The documentation should be restructured around one execution question:

`Should I continue, or should I stop for a human now?`

### `split-image-assets/SKILL.md`

Keep it as the high-level contract.

It should:

- state the default continuous execution model near the top
- define the five states
- define the two-layer event taxonomy
- define the stop eligibility rules
- define the grill-me style exit contract
- clearly separate commentary from formal gate behavior

It should stop trying to serve as the full procedural reference.

### `split-image-assets/references/workflow.md`

This should become the primary execution-routing reference.

Each major stage should explicitly state:

- default state
- whether pause is allowed
- pause category when allowed
- minimum evidence needed before stop
- continue behavior when pause is not allowed

The workflow doc should behave like a stateful runbook, not only a rich prose checklist.

### `split-image-assets/references/confirmation-prompts.md`

This should be reframed as a library of allowed stop templates.

Each prompt should map to:

- event class
- state
- stop condition
- recommended answer style
- effect on metadata

The file should not contain prompts for non-eligible pauses.

### `docs/usage/split-image-assets.md`

This should become the shortest operational entry point.

It should add:

- a concise “default execution model” section
- a “continue versus stop” quick table
- one happy path for continuous execution
- one example of a correct semantic-divergence stop
- one example of a true external blocker stop
- explicit anti-examples of progress-only pauses

## Metadata and Contract Alignment

This redesign is mostly about behavior, but some contract clarifications are required.

### Formal Metadata Principle

`decision_log` and `confirmation` are for formal state only.

They must not contain:

- progress updates
- “working on it” notes
- routine commentary
- stage summaries with no decision meaning

### Evidence Principle

If a stop is resolved through prior user intent rather than a fresh chat answer, the resolution must still be evidence-backed.

This reinforces:

- `explicit-user-confirmed`
- `inferred-from-user`

and keeps:

- `agent-defaulted`

out of any formal gate satisfaction path.

### Object-Scoped Semantic Divergence

When a semantic divergence is object-specific, the confirmation evidence should stay object-scoped.

This keeps one resolved ambiguity from incorrectly satisfying another object's branch.

## Script Alignment Requirements

This redesign does not require a new orchestrator in this phase, but it does require existing helpers and validation expectations to stay consistent with the interaction model.

Required alignment rules:

1. scripts that write formal decisions must preserve object-scoped evidence when the decision is object-specific
2. validators must enforce formal gates without treating commentary as gate evidence
3. packaging helpers must not make a valid non-pausing branch impossible
4. preview and manifest helpers must stay consistent with placeholder-only rebuild routing

This keeps the usability redesign from being only documentation deep.

## Test Strategy

The redesign should add or strengthen three classes of tests.

### 1. Stop Eligibility Tests

Validate that only these can produce a proactive stop:

- `user-decision`
- `external-blocker`
- `formal-approval`
- medium/high-risk semantic divergence

### 2. Non-Stop Continuation Tests

Validate that these continue with commentary:

- progress updates
- stage completion summaries
- warning-only audit results
- recoverable uncertainty
- evidence collection steps
- preview generation and validation passes/failures that still permit the next deterministic step

### 3. Exit Contract Tests

Validate that every allowed stop includes:

- why human input is required
- a recommendation
- option impact
- next action after confirmation

### 4. Gate Classification Regression Tests

Validate the mapped behavior for:

- `tooling_preflight`
- `granularity_alignment`
- `pilot_object`
- `approximate_reconstruction`
- `final_acceptance`
- `candidate_promotion`

## Acceptance Criteria

This redesign should be considered successful when:

1. `SKILL.md` explicitly describes the conservative continuous execution model
2. the workflow doc clearly distinguishes continue-only stages from stop-eligible stages
3. only hard events and medium/high-risk semantic divergence remain stop-eligible
4. progress commentary is explicitly barred from creating gate state
5. stop prompts follow a consistent recommendation-and-impact contract
6. tests exist to catch future regressions back into progress-driven pauses

## Risks and Trade-Offs

### Risk: Over-tightening stops

If the redesign is too strict, agents may continue through branches that should have been escalated.

Mitigation:

- allow medium/high-risk semantic divergence as an explicit stop class
- define concrete examples and anti-examples

### Risk: Documentation becomes even heavier

If the redesign only adds more prose, agent usability may get worse.

Mitigation:

- move from narrative prose toward explicit state/event tables
- keep `usage` short and execution-oriented

### Risk: Drift between docs and scripts

If documentation says “continue” but scripts or validators still force a contradictory path, the usability model fails.

Mitigation:

- require contract-alignment tests
- include script alignment as part of the redesign scope

## Implementation Phases

This design is intended to drive development directly.

### Phase 1: Execution Contract

- define the conservative continuous execution rule in `SKILL.md`
- define the five-state model
- define the two-layer event taxonomy
- define the stop eligibility rules
- define the grill-me style exit contract

### Phase 2: Workflow Reclassification

- rewrite `references/workflow.md` around state-aware stage behavior
- reclassify each existing gate
- remove implicit checkpoint-style stopping language

### Phase 3: Prompt and Usage Refactor

- rewrite `references/confirmation-prompts.md` as an allowed-stop prompt library
- rewrite `docs/usage/split-image-assets.md` around continue-versus-stop execution guidance

### Phase 4: Contract and Test Hardening

- align any remaining helper/validator behavior that contradicts the redesigned interaction model
- add regression tests for stop eligibility and stop contract structure

## Backlog After This Redesign

These items are intentionally deferred:

- a single-command orchestrator that chains the whole workflow
- further human-reader simplification for non-agent users
- broader skill-wide term compression and glossary work
- shared helper extraction for repeated interaction logic across scripts

## Summary

The main usability change is simple:

`split-image-assets` should stop acting like every meaningful step is a reason to stop talking and start acting like stopping is a rare, justified, well-structured exception.

That means:

- default execution continues
- commentary stays commentary
- only hard events and medium/high-risk semantic divergence may exit the workflow
- every exit must look like a real decision handoff, not a progress report

This preserves the package's rigor while making the execution model much more reliable for future agents.
