# Split Image Assets Granularity Gate Hardening Design

Date: 2026-07-05
Status: Draft for review
Target package: `split-image-assets`
Related bug report: `split-image-assets Bug Report: Granularity Gate Was Bypassed By Over-Broad Continuous Execution`

## Goal

Fix the workflow bug where broad autonomy instructions such as "continue", "use your default option", or "resources only, no text" can be over-read as permission to choose a specific resource family and micro-asset granularity for a dense composition.

The repaired workflow must:

1. keep conservative continuous execution as the default
2. keep the existing three stop classes only
3. make resource-family choice a first-class semantic gate output
4. tighten `inferred-from-user` so it requires exact branch specificity
5. add script- and validator-level guardrails so structurally valid but semantically wrong packages are harder to produce

This is a workflow-truth hardening pass, not a segmentation-model upgrade.

## Problem Summary

The reported failure pattern is:

1. the user gives broad autonomy
2. the source image contains multiple plausible non-text resource families
3. the agent selects one family silently
4. the workflow records that decision as `inferred-from-user`
5. the package becomes structurally valid but semantically wrong

The specific observed case was a rerun against a dense composition where the agent selected a narrow `right-rail hardware atoms` family and very fine micro-asset granularity without a true `Granularity Alignment Gate` stop.

## Root Cause

### Primary root cause

The current skill text does not operationalize strongly enough that:

- global autonomy is not semantic scope consent
- "keep going" does not resolve resource-family selection
- text-routing decisions do not resolve non-text package-family decisions

### Secondary root causes

1. `Granularity Alignment Gate` currently covers split scope, but not an explicit package-level `resource_family` selection.
2. `inferred-from-user` only requires durable evidence, not branch-specific evidence.
3. High-signal subset guidance can bias the agent toward tiny atoms before the intended family is settled.
4. Current script surfaces can record or preserve decision evidence, but they do not require enumeration of competing package families before broad plan execution.
5. Current validator truth focuses more on structural package honesty than on whether the selected family was explicitly resolved when dense-image ambiguity existed.

## Design Constraints

This pass must preserve:

- the current three allowed stop classes:
  - `user-decision`
  - `external-blocker`
  - `formal-approval`
- conservative continuous execution as the default
- no new "soft pause" or "progress pause" category
- existing route planning around `extract`, `reconstruct`, `generate`, `rebuild_downstream`, and `support_only`
- existing provider bridge and candidate lifecycle architecture

This pass must not:

- turn every dense image into an always-stop workflow
- treat all tiny assets as forbidden
- replace existing granularity fields with a brand-new planning model
- broaden the validator into an aesthetic or model-quality judge

## User-Confirmed Direction

The user selected the strongest version of the fix:

1. rule-layer hardening
2. data-contract hardening
3. validator/script-level guardrails
4. full regression coverage for the identified bug family

## Proposed Fix

The fix should ship in three layers, but as one bounded milestone.

### Layer 1: Rule Hardening

#### 1.1 Add an explicit anti-bypass rule

Add to `SKILL.md` near `Default Execution Contract` and `Decision Sync Rule`:

```text
Global autonomy instructions such as "continue", "use your default",
"do not stop unless needed", or "you decide" do not by themselves satisfy
Granularity Alignment Gate, Generation Routing Gate, Approximate
Reconstruction Acceptance Gate, Pilot Object Gate, Final Acceptance Gate,
or Candidate Promotion Acceptance Gate.

They only authorize continued execution after the current semantic branch
is already resolved.
```

#### 1.2 Tighten branch specificity for `inferred-from-user`

Revise the current `inferred-from-user` contract to:

```text
An inferred-from-user decision is valid only when the evidence resolves
the exact branch being recorded.
```

Concrete examples to add:

- valid: "split the right rail hardware lights first"
- invalid: "continue"
- invalid: "use your default"
- invalid: "resources only, no text" for non-text family selection

#### 1.3 Upgrade resource family into a required part of Granularity Alignment Gate

Clarify that for dense UI, poster, dashboard, or graphic compositions:

- a high-signal subset is not enough
- the package must also identify which non-text family it is targeting
- if multiple plausible families remain, the gate is unresolved

#### 1.4 Add a micro-asset trap rule

Add to asset value scoring and granularity guidance:

- small non-text objects are not automatically high-value
- under roughly 64 px, objects need an explicit value rationale
- if a package is dominated by tiny glyphs/status dots and the user did not explicitly request a micro-asset package, stop or downgrade those items to `support_only` / `draft-candidate`

### Layer 2: Data Contract Hardening

#### 2.1 Extend `metadata.granularity`

Add:

```json
"granularity": {
  "resource_family": "blueprint-modules | paper-scraps | right-rail-hardware | hero-ornaments | component-panels | other",
  "resource_family_confirmed": true,
  "resource_family_evidence_ref": "..."
}
```

Rules:

- `resource_family` is required for dense-image narrow packages
- `resource_family_confirmed=true` must not come from broad autonomy evidence
- `resource_family_evidence_ref` is required when `decision_source=inferred-from-user`

#### 2.2 Extend `plan_manifest.json`

Add `scope_selection`:

```json
"scope_selection": {
  "candidate_families": [
    {
      "family_id": "blueprint-modules",
      "why_it_is_valuable": "...",
      "typical_object_size": "medium",
      "expected_asset_count": 6,
      "expected_delivery_class": "clean-extraction",
      "excluded": false
    }
  ],
  "selected_family": "blueprint-modules",
  "selection_source": "explicit-user-confirmed | inferred-from-user | unresolved",
  "selection_evidence_ref": "...",
  "selection_notes": "..."
}
```

Rules:

- if more than one plausible family exists, `selected_family` cannot be silently chosen
- if the branch is unresolved, extraction must not widen past the gate
- `scope_selection` is planning truth, not final QA truth

### Layer 3: Runtime And Validation Guardrails

#### 3.1 `record_quality_review.py`

Enhance updates so that:

- `granularity.resource_family` can be recorded explicitly
- `resource_family_confirmed` and `resource_family_evidence_ref` are structured fields, not freeform notes
- `inferred-from-user` for granularity/resource-family decisions rejects weak evidence strings when the decision being written is a semantic family selection

This does not need to become NLP. A conservative denylist is acceptable for obvious weak evidence:

- `continue`
- `default option`
- `you decide`
- `project recommends narrow package`

#### 3.2 Planning helper / plan writer

Introduce either:

- a new `prepare_plan_manifest.py`, or
- a new shared planning helper used by existing planning entrypoints

That helper should:

- require `scope_selection.candidate_families[]`
- require `selected_family` or a formal unresolved-stop result
- fail closed when multiple plausible families exist and no exact family decision is recorded

This is the main workflow guardrail that prevents broad planning from being written too early.

#### 3.3 `validate_asset_package.py`

Add warning or blocking checks for:

1. dense UI package with `scope_strategy=high-signal-subset` but no `granularity.resource_family`
2. `granularity.user_confirmed=true` or `confirmation.granularity_alignment=confirmed` with `decision_source=inferred-from-user` and weak or non-specific evidence
3. package dominated by tiny assets but no explicit micro-asset rationale or family selection

The validator should stay evidence-oriented, not aesthetic. It should check:

- branch specificity
- missing family truth
- missing evidence for a claimed semantic narrowing

#### 3.4 Optional small helper: decision validation

If the main validator grows too noisy, add a narrow helper such as `validate_gate_decisions.py` that inspects semantic-gate decision entries before broader package validation.

## File-Level Change Plan

### Primary files

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `docs/usage/split-image-assets.md`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/scripts/validator_metadata_lib.py`
- `split-image-assets/scripts/validator_objects_lib.py`
- `split-image-assets/scripts/split_image_assets_contract.py`

### Candidate new helper

- `split-image-assets/scripts/prepare_plan_manifest.py`
  or
- a shared planning module if the current codebase already has a better fit

### Tests

- `split-image-assets/tests/test_processing_scripts.py`
- `split-image-assets/tests/test_validation_and_review.py`
- `split-image-assets/tests/test_docs_and_contract.py`

## Required Regression Tests

### Test A: Broad Autonomy Does Not Resolve Family

Context:

- user says "Continue until you need a decision."
- user says "Resources only, no text."
- source has multiple plausible non-text families

Expected:

- workflow stops at `Granularity Alignment Gate`
- no broad extraction or family-specific package is created before the answer

### Test B: Exact Family Instruction Allows Progress

Context:

- user says "Split the right rail hardware lights first."

Expected:

- `resource_family=right-rail-hardware` may be recorded
- planning and extraction may continue
- evidence is explicit and branch-specific

### Test C: Text Policy Does Not Resolve Family

Context:

- user says "Do not extract text, only resources."

Expected:

- `text_handling=rebuild_downstream` may be inferred
- `resource_family` remains unresolved if multiple non-text families exist

### Test D: Project Memory Suggests Candidate Families But Not Exact Selection

Context:

- project memory says future retries should use one of several narrow families

Expected:

- project memory may justify `narrow package`
- it does not justify a specific `selected_family`

### Test E: Tiny Glyph-Dominated Package Requires Explicit Scope

Context:

- package candidate list is dominated by under-64px glyphs or status dots

Expected:

- explicit micro-asset rationale or family selection required
- otherwise stop or downgrade

### Test F: Weak `inferred-from-user` Evidence Rejected

Context:

- semantic family decision is written with evidence ref that only says `continue`

Expected:

- review adapter rejects it
  or
- validator blocks it

## Rollout Strategy

### Phase 1

Ship rule and contract text first:

- `SKILL.md`
- workflow docs
- prompt docs
- contract docs

### Phase 2

Ship runtime enforcement:

- `record_quality_review.py`
- planning helper / manifest writer
- validator updates

### Phase 3

Ship regression suite and fixture updates.

This keeps the implementation bounded while still delivering the full fix package inside one milestone.

## Migration Notes

This pass will likely require compatibility handling for older packages that:

- have `granularity.mode` but no `resource_family`
- used `inferred-from-user` for broad autonomy phrases
- have dense-image narrow subsets but no `scope_selection`

Migration policy should be:

- older packages remain readable
- new packages and reruns use the stronger fields
- pass/approval claims on ambiguous new runs should not be grandfathered silently

## Success Criteria

The fix is complete when all of the following are true:

1. broad autonomy cannot be used as evidence for semantic family selection
2. dense-image narrow packages record an explicit `resource_family`
3. multi-family ambiguity causes a `user-decision` stop before extraction
4. text-routing evidence does not satisfy non-text family choice
5. tiny-glyph-dominated plans require explicit rationale or stop/downgrade
6. new regression tests cover the reported failure family
7. structurally valid but semantically misaligned packages become harder to produce through the default path

## Non-Goals

This fix does not:

- choose the best resource family automatically in every case
- prohibit micro-asset packages when explicitly requested
- replace the existing provider bridge design
- expand the visual quality audit into an AI semantic judge
- turn project memory into a forbidden input; it only limits what project memory is allowed to resolve

## Recommended Implementation Order

1. contract and docs
2. failing tests for the bug report scenarios
3. `record_quality_review.py` branch-specific evidence enforcement
4. `plan_manifest.scope_selection` writer and guardrails
5. validator warnings/blockers
6. fixture and regression cleanup

## Review Request

This document is intentionally strong on semantic gate correctness and intentionally conservative on automation.

The key review question is:

Should `resource_family` be mandatory only for dense-image high-signal-subset packages, or for every non-trivial planned package that narrows scope away from the full image?
