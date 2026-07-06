# Split Image Assets Planning Helper Depth V1 Design

Date: 2026-07-06
Status: Draft for review
Target package: `split-image-assets`

## Goal

Reduce the operator and agent burden of writing valid planning truth for `split-image-assets` without weakening the current truth gates.

This pass focuses on one narrow outcome:

- make `prepare_plan_manifest.py` the low-friction way to create and update `plan_manifest.scope_selection`

It does not change the validator's honesty rules. It lowers the cost of producing correct planning state.

## Problem Statement

After `granularity gate hardening V1`, the package now correctly treats:

- `resource_family`
- `scope_selection`
- unresolved multi-family ambiguity

as first-class truth.

That was the correct contract move, but it raised a workflow usability cost:

1. planning truth now requires more structured fields
2. the current helper path still expects the caller to know too much of that structure
3. incremental edits are easy to get wrong unless the operator already understands the whole planning schema

The result is not that the workflow is wrong. The result is that the workflow is correct but still heavier than it should be for ordinary planning updates.

## Scope

In scope:

- `split-image-assets/scripts/prepare_plan_manifest.py`
- `split-image-assets/scripts/package_state_lib.py`
- `split-image-assets/scripts/split_image_assets_contract.py`
- `split-image-assets/tests/test_processing_scripts.py`
- small usage/doc updates only if they are required to explain the new helper behavior

Out of scope:

- changing the `resource_family` validator semantics
- changing `record_quality_review.py`
- changing provider bridge behavior
- changing candidate lifecycle behavior
- adding a fully interactive wizard
- weakening any existing stop or truth gate

## Non-Goals

This pass should not:

- infer semantic scope that the workflow should still ask about
- auto-choose a family from broad autonomy instructions
- bypass unresolved multi-family stop-state
- make `plan_manifest.json` optional
- add a new pause class

## User-Confirmed Direction

The user selected the narrowest useful path:

- focus on reducing **planning input burden**
- use an **enhanced `prepare_plan_manifest.py`**
- keep the existing truth model and validator structure

## Design Summary

`prepare_plan_manifest.py` becomes the canonical write surface for `scope_selection`.

It should support three common planning states cleanly:

1. **single-family selected plan**
2. **multi-family unresolved stop-state**
3. **incremental update of an existing plan**

The helper should assemble the right JSON shape so callers do not have to hand-compose the `scope_selection` block every time.

## Proposed Behavior

### 1. Canonical write surface

`prepare_plan_manifest.py` should own writing:

- `scope_selection.candidate_families[]`
- `scope_selection.selected_family`
- `scope_selection.selection_source`
- `scope_selection.selection_evidence_ref`
- `scope_selection.selection_notes`

The helper should preserve existing values unless the caller explicitly replaces them.

### 2. Candidate family input ergonomics

The helper should accept simple repeated inputs for candidate families instead of requiring callers to hand-edit JSON.

Recommended CLI shape:

```text
--candidate-family <family-id>
--selected-family <family-id>
--selection-source <explicit-user-confirmed|inferred-from-user|unresolved>
--selection-evidence-ref <text>
--selection-note <text>
```

Approved ergonomic extension:

```text
--clear-candidate-families
--clear-selection
```

This is part of V1, not deferred. It keeps incremental edits explicit and avoids accidental resets.

### 3. Unresolved multi-family state remains first-class

When multiple plausible families exist, the helper must support writing an unresolved state deliberately.

That means:

- multiple `candidate_families[]` are allowed
- `selected_family` may remain empty
- `selection_source=unresolved` is valid
- the package can persist that ambiguity as planning truth

This is not a validation bypass. It is the package-owned record that the workflow reached a `user-decision` boundary and did not silently choose one branch.

### 4. Incremental updates must preserve old truth

If an existing plan already contains:

- `selected_family`
- `selection_source`
- `selection_evidence_ref`
- `selection_notes`

then a later helper call that only changes, for example, `candidate_families[]` or `selection_notes` must not wipe those fields unless the caller explicitly requests that.

This is the core usability improvement for V1.

### 4.1 Update semantics are explicit

V1 should use this write contract:

- omitted flag -> preserve existing value
- provided value -> replace existing value
- explicit clear flag -> reset the targeted field group

For this pass:

- `--clear-candidate-families` clears only `candidate_families[]`
- `--clear-selection` clears:
  - `selected_family`
  - `selection_source`
  - `selection_evidence_ref`
  - `selection_notes`

This avoids fake clears through empty strings or accidental resets through CLI defaults.

### 5. Weak autonomy rules stay untouched

`prepare_plan_manifest.py` may help write better planning truth, but it must not weaken the existing semantic-scope rules:

- broad autonomy phrases remain insufficient
- `inferred-from-user` still needs exact branch evidence
- validator and review-adapter enforcement remain authoritative

The helper is a convenience layer, not a shortcut around those rules.

## Data Model

This pass does not invent a new truth surface.

It continues using:

```json
"scope_selection": {
  "candidate_families": [
    {
      "family_id": "blueprint-modules",
      "why_it_is_valuable": "",
      "typical_object_size": "",
      "expected_asset_count": 0,
      "expected_delivery_class": "",
      "excluded": false
    }
  ],
  "selected_family": "",
  "selection_source": "unresolved",
  "selection_evidence_ref": "",
  "selection_notes": ""
}
```

V1 should only improve how that block gets assembled and updated.

## Implementation Strategy

### Layer 1: Contract-preserving helper ergonomics

Keep the current `default_scope_selection()` contract.

Add or refine helper utilities in `package_state_lib.py` so:

- `scope_selection` normalization is reusable
- incremental writes are explicit and predictable
- clearing versus preserving state is not ambiguous

### Layer 2: Smarter `prepare_plan_manifest.py`

Refactor the CLI around merge-style updates:

- read existing plan
- normalize current `scope_selection`
- apply only explicit CLI changes
- validate resulting state
- write back the updated manifest

### Layer 3: Regression coverage

Add tests that prove:

1. multi-family unresolved state can be persisted
2. explicit selected family is accepted
3. weak inferred evidence is still rejected
4. incremental note/family updates preserve prior selection state
5. explicit clearing resets state only when requested

## Acceptance Criteria

This pass is complete when:

1. `prepare_plan_manifest.py` can write a valid unresolved multi-family stop-state
2. `prepare_plan_manifest.py` can write a valid explicit selected family state
3. incremental updates no longer wipe valid prior selection fields unless explicitly told to
4. weak inferred evidence is still rejected
5. existing validator behavior remains green
6. the helper reduces field-by-field manual planning edits for ordinary cases

## Recommended Tests

### Test A: unresolved multi-family state persists

- write two candidate families
- leave `selected_family` empty
- set `selection_source=unresolved`
- assert the resulting plan persists the unresolved truth

### Test B: explicit selected family persists

- write two candidate families
- set one selected family
- set explicit source
- assert the exact choice is preserved

### Test C: incremental update preserves selected family

- create a plan with valid selection
- rerun helper changing only notes or candidate families
- assert prior selected fields remain intact

### Test D: weak inferred evidence still fails

- attempt `selection_source=inferred-from-user`
- provide only broad autonomy evidence
- assert helper fails closed

### Test E: explicit clear works

- start from valid selected family
- call helper with explicit clear flag
- assert selection fields are intentionally reset

## Risks

### 1. Silent merge bugs

If the helper preserves too much state implicitly, callers may think they replaced data when they only appended or merged.

Mitigation:

- use explicit clear flags
- keep update semantics documented
- add round-trip tests

### 2. Accidental truth weakening

If helper ergonomics tries to infer too much, it can reintroduce the semantic bypass that the last milestone just closed.

Mitigation:

- helper only assembles structure
- validator and review-adapter continue to police semantics

### 3. CLI sprawl

If too many planning fields are added in one pass, the helper becomes another heavy command instead of a simplification.

Mitigation:

- keep V1 focused on `scope_selection`
- postpone richer family metadata editing until a future milestone if it is not required now

## Recommendation

Implement V1 as a **small, contract-preserving helper upgrade**.

Do not broaden into:

- a wizard
- route planning automation
- provider-plan simplification

Those can be future milestones if needed.

## Decision

V1 includes explicit `--clear-candidate-families` and `--clear-selection` flags now.

The reason is straightforward:

- preserve-by-default alone lowers accidental overwrite risk
- explicit clear makes helper behavior predictable
- clear-versus-preserve should be encoded in the helper contract instead of being approximated through empty values or omitted fields
