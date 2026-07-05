# Task 3 Report: Planning Surface And Scope Selection Guard

## Status

DONE

## Requirements handled

- Added package-owned `scope_selection` truth to `plan_manifest.json` defaults.
- Added a fail-closed `prepare_plan_manifest.py` writer for scope-selection planning state.
- Enforced explicit `selected_family` for multi-family plans.
- Rejected weak inferred evidence such as broad autonomy phrases for semantic family selection.
- Preserved the existing three stop classes and did not change QA, candidate-promotion, generated-reconstruction, or provider-bridge gates.

## Files changed

- `E:\project\blog\awesome-skills\split-image-assets\scripts\package_state_lib.py`
- `E:\project\blog\awesome-skills\split-image-assets\scripts\prepare_plan_manifest.py`
- `E:\project\blog\awesome-skills\split-image-assets\scripts\split_image_assets_contract.py`
- `E:\project\blog\awesome-skills\split-image-assets\tests\test_processing_scripts.py`

## TDD evidence

### Red

Ran:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_init_asset_package_writes_default_scope_selection_to_plan_manifest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_requires_selected_family_when_multiple_families_exist split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_rejects_weak_inferred_selection_evidence split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_accepts_explicit_selected_family
```

Observed:

- `KeyError: 'scope_selection'` from initialized `plan_manifest.json`
- `prepare_plan_manifest.py` missing
- New plan-writer tests failed as expected

### Green

Re-ran the same focused test command after implementation and it passed:

```text
Ran 4 tests in 0.891s
OK
```

## Regression coverage

Ran:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_provider_request_selects_default_provider_when_omitted
```

Result:

```text
Ran 2 tests in 0.372s
OK
```

## Implementation summary

### `split_image_assets_contract.py`

- `default_plan_manifest(...)` now writes a default `scope_selection` block using `default_scope_selection()`.

### `package_state_lib.py`

- Added `normalize_scope_selection(...)` to keep the package scope-selection shape stable.
- Added `normalize_plan_manifest(...)` so reads and writes preserve the planning surface even for older manifests.
- Kept behavior conservative by only normalizing the new planning block.

### `prepare_plan_manifest.py`

- Added a new CLI that updates `plan_manifest.json` scope-selection state.
- Validates candidate families against `ALLOWED_RESOURCE_FAMILIES`.
- Fails closed when multiple candidate families are present without an explicit `selected_family`.
- Requires a non-`unresolved` `selection_source` when a family is selected.
- Rejects weak `inferred-from-user` evidence using `is_weak_autonomy_evidence(...)`.

### `test_processing_scripts.py`

- Added four Task 3 tests:
  - default manifest contains `scope_selection`
  - multi-family plan without `selected_family` fails
  - weak inferred evidence fails
  - explicit selected family succeeds and persists

## Commit

- `13bb307 feat: add scope selection planning guard`

## Self-review

- Verified the implementation stayed inside the four owned files plus this report.
- Checked that no new pause category was introduced.
- Confirmed the scope-selection guard only tightened ambiguous planning writes and did not touch downstream QA/provider/candidate gates.
- No blocking concerns found.

---

## 2026-07-05 Task 3 Review Fix Wave

### Scope

- Fix P1: allow package-owned unresolved multi-family planning state to persist.
- Fix P1: preserve existing scope-selection values during incremental writer updates unless the caller explicitly changes them.
- Keep the weak inferred-evidence rejection in place.

### Files changed

- `E:\project\blog\awesome-skills\split-image-assets\scripts\prepare_plan_manifest.py`
- `E:\project\blog\awesome-skills\split-image-assets\tests\test_processing_scripts.py`
- `E:\project\blog\awesome-skills\.superpowers\sdd\task-3-report.md`

### Red

Added failing tests first:

- `test_prepare_plan_manifest_persists_unresolved_multi_family_stop_state`
- `test_prepare_plan_manifest_preserves_existing_scope_selection_on_incremental_update`

Ran:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_persists_unresolved_multi_family_stop_state split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_rejects_weak_inferred_selection_evidence split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_accepts_explicit_selected_family split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_preserves_existing_scope_selection_on_incremental_update
```

Observed:

- unresolved multi-family planning still failed with `scope_selection.selected_family is required when multiple candidate families exist`
- incremental note-only update wiped prior valid selection state and failed on the same guard

Red result:

```text
Ran 4 tests in 1.109s
FAILED (failures=2)
```

### Green

Implemented the minimal fix in `prepare_plan_manifest.py`:

- removed the hard failure for unresolved multi-family candidate sets
- changed CLI option defaults from concrete values to `None`
- only overwrote `scope_selection` fields when the caller actually supplied that flag

Re-ran the same focused command:

```text
Ran 4 tests in 1.076s
OK
```

### Broader regression

Ran:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_init_asset_package_writes_default_scope_selection_to_plan_manifest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields
```

Result:

```text
Ran 2 tests in 0.179s
OK
```

### Behavior summary

- `prepare_plan_manifest.py` can now persist an unresolved multi-family stop-state as package-owned truth.
- Incremental writes now preserve prior `candidate_families`, `selected_family`, `selection_source`, and `selection_evidence_ref` unless those flags are explicitly supplied again.
- Weak `inferred-from-user` evidence is still rejected.

### Commit

- `fix: preserve task 3 scope selection state`
