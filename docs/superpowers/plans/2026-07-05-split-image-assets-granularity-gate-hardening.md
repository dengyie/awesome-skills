# Split Image Assets Granularity Gate Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden `split-image-assets` so broad autonomy instructions cannot bypass `Granularity Alignment Gate`, resource-family choice becomes explicit package truth, and dense-image semantic narrowing fails closed when the exact branch is unresolved.

**Architecture:** Add one shared semantic-scope contract layer, then wire it through the review adapter, planning surface, and validator. Keep the existing planning-first / provider-bridge / candidate-lifecycle architecture intact, and tighten only the semantic-scope truth path needed to prevent silent family selection.

**Tech Stack:** Python, `unittest`, JSON package manifests, existing `split-image-assets` script/validator/doc surface

## Global Constraints

- Preserve the current three allowed stop classes exactly: `user-decision`, `external-blocker`, `formal-approval`.
- Keep conservative continuous execution as the default execution model.
- Do not add a new pause category or reintroduce progress-only pauses.
- Do not weaken current truth gates for `qa.status`, candidate promotion, generated reconstruction, or provider bridge behavior.
- Treat broad autonomy phrases such as `continue`, `use your default`, `you decide`, and `do not stop unless needed` as insufficient evidence for semantic branch selection.
- Make `resource_family` first-class package truth for dense-image narrow packages.
- Add failing tests before production code for each behavior change.

---

## File Map

- Modify: `E:/project/blog/awesome-skills/split-image-assets/SKILL.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/workflow.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/confirmation-prompts.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/asset-package-contract.md`
- Modify: `E:/project/blog/awesome-skills/docs/usage/split-image-assets.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/split_image_assets_contract.py`
- Create: `E:/project/blog/awesome-skills/split-image-assets/scripts/semantic_scope_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/record_quality_review.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/package_state_lib.py`
- Create: `E:/project/blog/awesome-skills/split-image-assets/scripts/prepare_plan_manifest.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validate_asset_package.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validator_metadata_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validator_objects_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/tests/test_docs_and_contract.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/tests/test_processing_scripts.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/tests/test_validation_and_review.py`

## Task 1: Rule And Contract Surface

**Files:**
- Create: `E:/project/blog/awesome-skills/split-image-assets/scripts/semantic_scope_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/split_image_assets_contract.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/SKILL.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/workflow.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/confirmation-prompts.md`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/references/asset-package-contract.md`
- Modify: `E:/project/blog/awesome-skills/docs/usage/split-image-assets.md`
- Test: `E:/project/blog/awesome-skills/split-image-assets/tests/test_docs_and_contract.py`

**Interfaces:**
- Consumes: existing `split_image_assets_contract.py` enums and default manifest helpers
- Produces:
  - `ALLOWED_RESOURCE_FAMILIES: set[str]`
  - `WEAK_AUTONOMY_EVIDENCE_MARKERS: tuple[str, ...]`
  - `default_scope_selection() -> dict`
  - `is_weak_autonomy_evidence(evidence_ref: str) -> bool`
  - doc-level rule text for semantic branch specificity

- [ ] **Step 1: Write the failing doc/contract tests**

```python
def test_skill_docs_forbid_broad_autonomy_as_semantic_scope_evidence(self):
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("Global autonomy instructions", skill_text)
    self.assertIn("do not by themselves satisfy", skill_text)
    self.assertIn("resource_family", skill_text)


def test_shared_contract_exposes_resource_family_scope_fields(self):
    contract = self._load_script_module("split_image_assets_contract.py")
    self.assertIn("blueprint-modules", contract.ALLOWED_RESOURCE_FAMILIES)
    self.assertIn("right-rail-hardware", contract.ALLOWED_RESOURCE_FAMILIES)
    scope = contract.default_scope_selection()
    self.assertEqual(scope["selected_family"], "")
    self.assertEqual(scope["selection_source"], "unresolved")
```

- [ ] **Step 2: Run the doc/contract tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_skill_docs_forbid_broad_autonomy_as_semantic_scope_evidence split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields
```

Expected: FAIL because the current docs do not yet contain the new anti-bypass wording and the contract does not yet expose resource-family helpers.

- [ ] **Step 3: Implement the shared semantic-scope contract surface**

```python
# split-image-assets/scripts/split_image_assets_contract.py
ALLOWED_RESOURCE_FAMILIES = {
    "blueprint-modules",
    "paper-scraps",
    "right-rail-hardware",
    "hero-ornaments",
    "component-panels",
    "other",
}


def default_scope_selection() -> dict:
    return {
        "candidate_families": [],
        "selected_family": "",
        "selection_source": "unresolved",
        "selection_evidence_ref": "",
        "selection_notes": "",
    }
```

```python
# split-image-assets/scripts/semantic_scope_lib.py
WEAK_AUTONOMY_EVIDENCE_MARKERS = (
    "continue",
    "default option",
    "use your default",
    "you decide",
    "do not stop unless needed",
    "project recommends narrow package",
)


def is_weak_autonomy_evidence(evidence_ref: str) -> bool:
    normalized = str(evidence_ref or "").strip().lower()
    return any(marker in normalized for marker in WEAK_AUTONOMY_EVIDENCE_MARKERS)
```

Also patch the docs so they explicitly state:

- global autonomy does not satisfy semantic gates
- `resource_family` is part of `Granularity Alignment Gate`
- `inferred-from-user` must resolve the exact branch being recorded
- high-signal subset examples do not grant permission to choose a micro-asset package

- [ ] **Step 4: Re-run the doc/contract tests to verify they pass**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_skill_docs_forbid_broad_autonomy_as_semantic_scope_evidence split-image-assets.tests.test_docs_and_contract.SplitImageAssetsPackageTests.test_shared_contract_exposes_resource_family_scope_fields
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/SKILL.md split-image-assets/references/workflow.md split-image-assets/references/confirmation-prompts.md split-image-assets/references/asset-package-contract.md docs/usage/split-image-assets.md split-image-assets/scripts/split_image_assets_contract.py split-image-assets/scripts/semantic_scope_lib.py split-image-assets/tests/test_docs_and_contract.py
git commit -m "feat: add semantic scope contract"
```

### Task 2: Review Adapter Scope Enforcement

**Files:**
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/record_quality_review.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/split_image_assets_contract.py`
- Create: `E:/project/blog/awesome-skills/split-image-assets/scripts/semantic_scope_lib.py`
- Test: `E:/project/blog/awesome-skills/split-image-assets/tests/test_validation_and_review.py`

**Interfaces:**
- Consumes:
  - `ALLOWED_RESOURCE_FAMILIES`
  - `default_scope_selection()`
  - `is_weak_autonomy_evidence(evidence_ref: str) -> bool`
- Produces:
  - `metadata.granularity.resource_family`
  - `metadata.granularity.resource_family_confirmed`
  - `metadata.granularity.resource_family_evidence_ref`
  - branch-specific rejection of weak `inferred-from-user` evidence for semantic family selection

- [ ] **Step 1: Write the failing review-adapter tests**

```python
def test_record_quality_review_rejects_weak_inferred_resource_family_evidence(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "record_quality_review.py"),
            str(output),
            "--granularity-mode", "atomic-layer",
            "--resource-family", "right-rail-hardware",
            "--resource-family-confirmed",
            "--confirmation-key", "granularity_alignment",
            "--confirmation-status", "confirmed",
            "--confirmation-source", "inferred-from-user",
            "--pause-category", "user-decision",
            "--evidence-ref", "user said continue",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("exact branch", result.stderr)


def test_record_quality_review_accepts_explicit_resource_family_evidence(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "record_quality_review.py"),
            str(output),
            "--granularity-mode", "atomic-layer",
            "--resource-family", "right-rail-hardware",
            "--resource-family-confirmed",
            "--confirmation-key", "granularity_alignment",
            "--confirmation-status", "confirmed",
            "--confirmation-source", "explicit-user-confirmed",
            "--pause-category", "user-decision",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
```

- [ ] **Step 2: Run the review-adapter tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence
```

Expected: FAIL because the CLI does not yet support `resource_family` fields or weak-evidence rejection.

- [ ] **Step 3: Implement resource-family fields and branch-specific evidence enforcement**

```python
# record_quality_review.py
parser.add_argument("--resource-family", choices=sorted(ALLOWED_RESOURCE_FAMILIES))
parser.add_argument("--resource-family-confirmed", action="store_true")
parser.add_argument("--resource-family-evidence-ref", default="")
```

```python
def update_granularity(metadata: dict, args: argparse.Namespace) -> None:
    granularity = metadata.setdefault("granularity", {})
    if args.resource_family is not None:
        granularity["resource_family"] = args.resource_family
    if args.resource_family_confirmed:
        granularity["resource_family_confirmed"] = True
    if args.resource_family_evidence_ref:
        granularity["resource_family_evidence_ref"] = args.resource_family_evidence_ref
```

```python
def require_branch_specific_scope_evidence(
    decision_source: str,
    evidence_ref: str,
    resource_family: str,
) -> None:
    if decision_source != "inferred-from-user":
        return
    if is_weak_autonomy_evidence(evidence_ref):
        raise ValueError(
            "inferred-from-user evidence must resolve the exact branch being recorded for resource_family"
        )
    if resource_family and resource_family not in str(evidence_ref).lower():
        raise ValueError(
            "inferred-from-user evidence must resolve the exact branch being recorded for resource_family"
        )
```

Invoke that enforcement whenever `granularity_alignment` or a semantic family decision is being recorded.

- [ ] **Step 4: Re-run the review-adapter tests to verify they pass**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_rejects_weak_inferred_resource_family_evidence split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_record_quality_review_accepts_explicit_resource_family_evidence
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/scripts/record_quality_review.py split-image-assets/scripts/split_image_assets_contract.py split-image-assets/scripts/semantic_scope_lib.py split-image-assets/tests/test_validation_and_review.py
git commit -m "feat: enforce branch-specific scope evidence"
```

### Task 3: Planning Surface And Scope Selection Guard

**Files:**
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/package_state_lib.py`
- Create: `E:/project/blog/awesome-skills/split-image-assets/scripts/prepare_plan_manifest.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/split_image_assets_contract.py`
- Test: `E:/project/blog/awesome-skills/split-image-assets/tests/test_processing_scripts.py`

**Interfaces:**
- Consumes:
  - `default_scope_selection()`
  - `default_plan_manifest(...)`
- Produces:
  - `plan_manifest["scope_selection"]`
  - `prepare_plan_manifest.py`
  - fail-closed scope-selection validation for multi-family plans

- [ ] **Step 1: Write the failing planning tests**

```python
def test_prepare_plan_manifest_requires_selected_family_when_multiple_families_exist(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--candidate-family", "blueprint-modules",
            "--candidate-family", "paper-scraps",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("selected_family", result.stderr)


def test_prepare_plan_manifest_accepts_explicit_selected_family(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--candidate-family", "blueprint-modules",
            "--candidate-family", "paper-scraps",
            "--selected-family", "blueprint-modules",
            "--selection-source", "explicit-user-confirmed",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
```

- [ ] **Step 2: Run the planning tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_requires_selected_family_when_multiple_families_exist split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_accepts_explicit_selected_family
```

Expected: FAIL because the helper does not yet exist.

- [ ] **Step 3: Implement `scope_selection` and the plan writer**

```python
# split_image_assets_contract.py
def default_plan_manifest(source_path: str, package_name: str, width: int, height: int) -> dict:
    return {
        ...
        "scope_selection": default_scope_selection(),
        "objects": [],
        ...
    }
```

```python
# prepare_plan_manifest.py
def validate_scope_selection(payload: dict) -> None:
    families = payload["candidate_families"]
    selected_family = payload["selected_family"]
    if len(families) > 1 and not selected_family:
        raise ValueError("scope_selection.selected_family is required when multiple candidate families exist")
```

```python
def main() -> int:
    # load existing plan_manifest.json
    # update scope_selection.candidate_families[]
    # require selected family or unresolved stop result
    # write plan manifest back
```

- [ ] **Step 4: Re-run the planning tests to verify they pass**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_requires_selected_family_when_multiple_families_exist split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_accepts_explicit_selected_family
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/scripts/package_state_lib.py split-image-assets/scripts/prepare_plan_manifest.py split-image-assets/scripts/split_image_assets_contract.py split-image-assets/tests/test_processing_scripts.py
git commit -m "feat: add scope selection planning guard"
```

### Task 4: Validator And Regression Gate

**Files:**
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validate_asset_package.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validator_metadata_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/validator_objects_lib.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/tests/test_validation_and_review.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/tests/test_processing_scripts.py`

**Interfaces:**
- Consumes:
  - `metadata.granularity.resource_family`
  - `metadata.granularity.resource_family_confirmed`
  - `metadata.granularity.resource_family_evidence_ref`
  - `plan_manifest.scope_selection`
  - `is_weak_autonomy_evidence(...)`
- Produces:
  - validation errors for unresolved semantic-family narrowing
  - validation errors for weak `inferred-from-user` family evidence
  - validation errors for micro-asset-dominated narrow packages without explicit rationale

- [ ] **Step 1: Write the failing validator tests**

```python
def test_validate_asset_package_rejects_dense_subset_without_resource_family(self):
    metadata["granularity"]["scope_strategy"] = "high-signal-subset"
    metadata["granularity"]["resource_family"] = ""
    errors = validator.collect_validation_errors(output, metadata)
    self.assertTrue(any("resource_family" in error for error in errors))


def test_validate_asset_package_rejects_weak_inferred_resource_family_evidence(self):
    metadata["granularity"]["resource_family"] = "right-rail-hardware"
    metadata["granularity"]["resource_family_confirmed"] = True
    metadata["granularity"]["resource_family_evidence_ref"] = "continue"
    metadata["confirmation"]["granularity_alignment"]["source"] = "inferred-from-user"
    errors = validator.collect_validation_errors(output, metadata)
    self.assertTrue(any("exact branch" in error for error in errors))
```

- [ ] **Step 2: Run the validator tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_subset_without_resource_family split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_weak_inferred_resource_family_evidence
```

Expected: FAIL because the validator does not yet enforce those conditions.

- [ ] **Step 3: Implement validator guardrails**

```python
# validator_metadata_lib.py or validate_asset_package.py
if is_dense_high_signal_subset and not resource_family:
    errors.append("granularity.resource_family is required for dense high-signal-subset packages")

if decision_source == "inferred-from-user" and is_weak_autonomy_evidence(resource_family_evidence_ref):
    errors.append("inferred-from-user evidence must resolve the exact branch being recorded for resource_family")
```

```python
# validator_objects_lib.py
if tiny_asset_count >= 3 and resource_family == "" and not micro_asset_rationale:
    errors.append("micro-asset-dominated package requires explicit resource-family or value rationale")
```

- [ ] **Step 4: Re-run the validator tests and full package suite**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_dense_subset_without_resource_family split-image-assets.tests.test_validation_and_review.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_weak_inferred_resource_family_evidence
$env:PYTHONUTF8='1'; python -B -m unittest discover split-image-assets\tests -v
$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets
```

Expected:
- targeted tests PASS
- full suite PASS
- `Skill is valid!`

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/scripts/validate_asset_package.py split-image-assets/scripts/validator_metadata_lib.py split-image-assets/scripts/validator_objects_lib.py split-image-assets/tests/test_validation_and_review.py split-image-assets/tests/test_processing_scripts.py
git commit -m "fix: harden granularity scope validation"
```

## Spec Coverage Check

- Rule-layer hardening: covered by Task 1
- Data-contract hardening for `resource_family` and `scope_selection`: covered by Tasks 1 and 3
- `record_quality_review.py` enforcement: covered by Task 2
- validator/script-level guardrails: covered by Task 4
- regression tests A-F from the design: Tasks 2-4 cover them directly

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-05-split-image-assets-granularity-gate-hardening.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
