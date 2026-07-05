# Task 2 Report: Review Adapter Scope Enforcement

## Status
- Done

## Requirements Source
- `E:\project\blog\awesome-skills\.superpowers\sdd\task-2-brief.md`

## Scope Completed
- Added failing tests first for the Task 2 review-adapter behavior.
- Verified the focused red run failed before production changes.
- Implemented review-adapter `resource_family` recording and narrow inferred-evidence enforcement.
- Re-ran the focused tests and the full `split-image-assets.tests.test_validation_and_review` module.
- Committed the code change.
- Performed a scoped self-review against the diff and task constraints.

## Red-Green Evidence
### Red
- Command:
  - `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence`
- Result:
  - Failed as expected before implementation because `record_quality_review.py` did not recognize `--resource-family` / `--resource-family-confirmed`.

### Green
- Command:
  - `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence`
- Result:
  - Passed after implementation.

## Code Changes
### `split-image-assets/scripts/record_quality_review.py`
- Added CLI flags:
  - `--resource-family`
  - `--resource-family-confirmed`
  - `--resource-family-evidence-ref`
- Persisted:
  - `metadata.granularity.resource_family`
  - `metadata.granularity.resource_family_confirmed`
  - `metadata.granularity.resource_family_evidence_ref`
- Added a narrow `require_branch_specific_scope_evidence(...)` guard that:
  - only runs for `inferred-from-user`
  - only applies when semantic family truth is being recorded
  - rejects weak autonomy evidence using `is_weak_autonomy_evidence(...)`
  - rejects evidence that does not name the exact `resource_family` branch
- Added small input guards:
  - `--resource-family-confirmed` requires `--resource-family`
  - `--resource-family-evidence-ref` requires `--resource-family`

### `split-image-assets/tests/test_validation_and_review.py`
- Added:
  - `test_record_quality_review_rejects_weak_inferred_resource_family_evidence`
  - `test_record_quality_review_accepts_explicit_resource_family_evidence`

## Constraints Check
- Preserved the three allowed stop classes exactly:
  - `user-decision`
  - `external-blocker`
  - `formal-approval`
- Kept conservative continuous execution as the default.
- Did not add a new pause category.
- Did not weaken:
  - `qa.status` gates
  - candidate promotion gates
  - generated reconstruction gates
  - provider bridge behavior
- Treated broad autonomy phrases as insufficient evidence for semantic branch selection.
- Kept `resource_family` as explicit package truth when recorded through the review adapter.

## Validation
- `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence`
  - 2 tests passed
- `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review -v`
  - 95 tests passed

## Commit
- `e2c4cf4 feat: enforce branch-specific scope evidence`

## Self-Review
- The enforcement is intentionally narrow: it only hardens semantic family writes and does not interfere with existing inferred granularity confirmation cases that do not record a family branch.
- The change is scoped to the review adapter and its tests, which matches Task 2 and avoids collateral contract or validator drift.
- No additional concerns were found after diff review.

---

## Review Fix Wave 2: Decision-Stage Granularity Alignment Bypass

### Status
- Done

### Reviewer Finding
- Weak inferred evidence was still accepted when semantic family truth was recorded through `--decision-stage granularity-alignment`, because the branch-specific guard only inspected `--confirmation-source`.

### Red Evidence
- Added failing regression:
  - `split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence_via_decision_stage`
- Command:
  - `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence_via_decision_stage`
- Result before fix:
  - Failed red as expected.
  - Assertion: the CLI returned `0` for the reproduced `--decision-stage granularity-alignment` + `--decision-source inferred-from-user` + weak `--evidence-ref "user said continue"` flow, proving the bypass.

### Root Cause
- `record_quality_review.py` ran `require_branch_specific_scope_evidence(...)` only against `args.confirmation_source`.
- The `--decision-stage granularity-alignment` path writes semantic family truth through `args.decision_source`, so that branch never passed through the same guard.

### Fix Applied
#### `split-image-assets/scripts/record_quality_review.py`
- Kept the existing confirmation-path guard.
- Added the same `require_branch_specific_scope_evidence(...)` check for `args.decision_source` when `args.decision_stage == "granularity-alignment"`.
- Kept the change narrow to the semantic-family decision-stage path; no broader confirmation or QA behavior changed.

#### `split-image-assets/tests/test_validation_and_review.py`
- Added:
  - `test_record_quality_review_rejects_weak_inferred_resource_family_evidence_via_decision_stage`

### Green Evidence
- Focused command:
  - `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence_via_decision_stage split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence`
- Focused result:
  - 3 tests passed.
- Broader regression command:
  - `$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review -v`
- Broader regression result:
  - 96 tests passed.

### Commit
- `ff5f550 fix: close decision-stage scope evidence bypass`

### Concerns
- None.
