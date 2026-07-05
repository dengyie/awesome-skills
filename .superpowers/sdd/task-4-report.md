# Task 4 Report: Validator And Regression Gate

## Scope

- Wrote failing Task 4 validator regressions first.
- Hardened validator enforcement for semantic-family narrowing on dense high-signal-subset packages.
- Added regression coverage for weak inferred semantic-family evidence and micro-asset-dominated narrow packages.
- Kept the existing stop classes and current QA/promotion/generated/provider gates unchanged.

## Files Changed

- `split-image-assets/scripts/validate_asset_package.py`
- `split-image-assets/scripts/validator_metadata_lib.py`
- `split-image-assets/scripts/validator_objects_lib.py`
- `split-image-assets/tests/test_validation_and_review.py`
- `split-image-assets/tests/test_environment_and_init.py`

## Red Phase

Added failing tests for:

1. Dense high-signal-subset UI package with no `granularity.resource_family`
2. Weak `inferred-from-user` evidence for recorded `resource_family`
3. Micro-asset-dominated narrow package with no explicit family or value rationale

Focused red verification:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_subset_without_resource_family split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_micro_asset_dominated_narrow_package_without_rationale
```

Observed result before implementation: all three tests failed for missing Task 4 validator behavior.

## Implementation

### `validator_metadata_lib.py`

- `validate_metadata_fields(...)` now accepts `plan_manifest`
- validates `granularity.resource_family*` field shapes
- requires `granularity.resource_family` for dense UI-like `high-signal-subset` packages
- emits an unresolved semantic-family narrowing error when that package truth is still missing and `plan_manifest.scope_selection.selected_family` is empty
- rejects weak or branch-nonspecific `inferred-from-user` evidence when `resource_family` is being recorded

### `validator_objects_lib.py`

- detects micro-asset-dominated `high-signal-subset` packages
- rejects those packages when neither explicit `resource_family` truth nor explicit value rationale is present

### `validate_asset_package.py`

- threads `plan_manifest` into metadata validation so semantic-family checks can use package planning truth

### Test Alignment

- updated the existing UI atomic acceptance fixture so it records first-class `resource_family` package truth
- aligned the `package_state_lib` test with normalized `scope_selection` behavior already written by the helper

## Verification

Focused Task 4 tests:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_subset_without_resource_family split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_micro_asset_dominated_narrow_package_without_rationale
```

Result: pass

Broader regression:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest discover split-image-assets\tests -v
```

Result: 270 tests passed

Package validation:

```powershell
$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets
```

Result: `Skill is valid!`

## Self-Review

- The new validator logic is scoped to dense `high-signal-subset` narrowing and inferred semantic-family truth only.
- Existing stop taxonomy remains exactly `user-decision`, `external-blocker`, and `formal-approval`.
- No current QA, candidate promotion, generated reconstruction, or provider bridge guard was relaxed.
- The broader suite stayed green after updating the existing UI atomic fixture to carry the new first-class package truth.

## Concerns

- None at completion.

## Commit

- `fix: harden granularity scope validation`

---

## Task 4 Fix Wave 2: Broaden Dense Non-UI Narrow-Package Resource Family Guard

### Review Finding

- The new `resource_family` validator path was too narrow: it only enforced the guard for `is_ui_like_package(...)`, while the Task 4 design/plan scope is broader and covers dense-image narrow `high-signal-subset` packages generally.

### Scope Of This Fix

- Kept the existing UI-path enforcement intact.
- Broadened the validator so `resource_family` is also required when a `high-signal-subset` package already records dense semantic-family narrowing intent through `plan_manifest.scope_selection`.
- Added a regression for a dense non-UI narrow package with multiple plausible candidate families and no recorded `resource_family`.

### Files Changed

- `split-image-assets/scripts/validator_metadata_lib.py`
- `split-image-assets/tests/test_validation_and_review.py`

### Red Evidence

New failing regression added first:

- `test_validate_asset_package_rejects_dense_non_ui_subset_without_resource_family`

Focused red command:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_non_ui_subset_without_resource_family
```

Observed result before implementation:

- FAIL
- validator returned success (`0 == 0`) for a non-UI `high-signal-subset` package whose `plan_manifest.scope_selection` still showed unresolved family narrowing and whose `granularity.resource_family` was empty

### Implementation

#### `validator_metadata_lib.py`

- Preserved the existing UI-like gate exactly as part of the broader condition.
- Added `candidate_families` detection from `plan_manifest.scope_selection`.
- Broadened the `resource_family` requirement so it now triggers for `high-signal-subset` packages when either:
  - the package is UI-like, or
  - planning truth already records semantic-family narrowing context through non-empty `candidate_families`, or
  - a `selected_family` is already present
- Kept the validator fail-closed by preserving the unresolved-family error when `selected_family` is still empty.

#### `test_validation_and_review.py`

- Reworked the prior dense-subset regression into a true non-UI scenario:
  - non-UI `visual_hierarchy`
  - non-UI object metadata
  - `plan_manifest.scope_selection.candidate_families = ["blueprint-modules", "paper-scraps"]`
  - empty `granularity.resource_family`

### Green Evidence

Focused Task 4 command:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_non_ui_subset_without_resource_family split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_micro_asset_dominated_narrow_package_without_rationale
```

Result:

- PASS (`Ran 3 tests`)

Minimum broader regression:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review -v
```

Result:

- PASS (`Ran 101 tests`)

### Self-Review

- The fix does not weaken the existing UI-path checks; it widens the same guard to include non-UI dense narrow packages when planning truth already says semantic-family narrowing is in play.
- No other validator domains were relaxed.
- `split-image-assets/tests/test_processing_scripts.py` was not needed for this review finding because the missing coverage and the behavior change both live in package validation.
