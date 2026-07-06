# Split Image Assets Planning Helper Depth V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `prepare_plan_manifest.py` a lower-friction helper for writing `scope_selection` truth, with preserve-by-default updates and explicit clear semantics.

**Architecture:** Keep the current `scope_selection` truth model and validator semantics intact. Improve only the helper/write path by making update behavior explicit: omitted flags preserve, provided flags replace, and clear flags reset targeted state. Use `package_state_lib.py` as the normalization layer and keep `prepare_plan_manifest.py` as the canonical writer surface.

**Tech Stack:** Python, `unittest`, existing `split-image-assets` planning helpers and manifest contract

## Global Constraints

- Do not change validator meaning for semantic-family truth in this milestone.
- Do not weaken the current `resource_family` / `scope_selection` contract.
- Do not add a wizard, new pause class, or route auto-selection logic.
- Preserve conservative continuous execution and the current three stop classes exactly.
- Helper semantics must be explicit:
  - omitted flag -> preserve
  - provided value -> replace
  - explicit clear flag -> reset targeted field group
- Add failing tests before production code for each behavior change.

---

### Task 1: Clear-Safe Scope Selection Helper

**Files:**
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/prepare_plan_manifest.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/package_state_lib.py`
- Test: `E:/project/blog/awesome-skills/split-image-assets/tests/test_processing_scripts.py`

**Interfaces:**
- Consumes:
  - `normalize_scope_selection(...)`
  - existing `scope_selection` block from `plan_manifest.json`
- Produces:
  - `--clear-candidate-families`
  - `--clear-selection`
  - preserve-by-default update behavior

- [ ] **Step 1: Write the failing tests**

```python
def test_prepare_plan_manifest_clear_candidate_families_only(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--clear-candidate-families",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan = json.loads((output / "plan_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(plan["scope_selection"]["candidate_families"], [])
    self.assertEqual(plan["scope_selection"]["selected_family"], "blueprint-modules")


def test_prepare_plan_manifest_clear_selection_only(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--clear-selection",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan = json.loads((output / "plan_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(plan["scope_selection"]["selected_family"], "")
    self.assertEqual(plan["scope_selection"]["selection_source"], "unresolved")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_candidate_families_only split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_selection_only
```

Expected: FAIL because the CLI does not yet support explicit clear semantics.

- [ ] **Step 3: Implement the minimal helper changes**

```python
# prepare_plan_manifest.py
parser.add_argument("--clear-candidate-families", action="store_true")
parser.add_argument("--clear-selection", action="store_true")
```

```python
def apply_scope_selection_update(existing: dict, args: argparse.Namespace) -> dict:
    scope = normalize_scope_selection(existing)
    if args.clear_candidate_families:
        scope["candidate_families"] = []
    if args.clear_selection:
        scope["selected_family"] = ""
        scope["selection_source"] = "unresolved"
        scope["selection_evidence_ref"] = ""
        scope["selection_notes"] = ""
    # then apply explicit replacement args only
    return scope
```

Use the same preserve-by-default behavior for all non-cleared fields.

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_candidate_families_only split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_selection_only
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/scripts/prepare_plan_manifest.py split-image-assets/scripts/package_state_lib.py split-image-assets/tests/test_processing_scripts.py
git commit -m "feat: add explicit scope selection clear paths"
```

### Task 2: Round-Trip Planning Safety

**Files:**
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/prepare_plan_manifest.py`
- Modify: `E:/project/blog/awesome-skills/split-image-assets/scripts/package_state_lib.py`
- Test: `E:/project/blog/awesome-skills/split-image-assets/tests/test_processing_scripts.py`

**Interfaces:**
- Consumes:
  - existing `scope_selection` state
  - clear flags and replacement args
- Produces:
  - predictable round-trip behavior for additive/preservative updates

- [ ] **Step 1: Write the failing tests**

```python
def test_prepare_plan_manifest_preserves_selection_when_adding_note(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--selection-note",
            "added note only",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan = json.loads((output / "plan_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(plan["scope_selection"]["selected_family"], "blueprint-modules")
    self.assertEqual(plan["scope_selection"]["selection_source"], "explicit-user-confirmed")


def test_prepare_plan_manifest_clear_then_replace_selection(self):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_plan_manifest.py"),
            str(output),
            "--clear-selection",
            "--selected-family",
            "paper-scraps",
            "--selection-source",
            "explicit-user-confirmed",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    plan = json.loads((output / "plan_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(plan["scope_selection"]["selected_family"], "paper-scraps")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_preserves_selection_when_adding_note split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_then_replace_selection
```

Expected: FAIL because current update semantics are not yet fully round-trip-safe.

- [ ] **Step 3: Implement the minimal round-trip fixes**

```python
def merge_scope_selection(existing: dict, args: argparse.Namespace) -> dict:
    scope = apply_scope_selection_update(existing, args)
    # explicit replacements happen after clear
    if args.selected_family is not None:
        scope["selected_family"] = args.selected_family
    if args.selection_source is not None:
        scope["selection_source"] = args.selection_source
    if args.selection_evidence_ref is not None:
        scope["selection_evidence_ref"] = args.selection_evidence_ref
    if args.selection_note is not None:
        scope["selection_notes"] = args.selection_note
    return scope
```

Keep validation after merge, not before.

- [ ] **Step 4: Run focused and broader regressions**

Run:

```powershell
$env:PYTHONUTF8='1'; python -B -m unittest split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_preserves_selection_when_adding_note split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_clear_then_replace_selection split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_persists_unresolved_multi_family_stop_state split-image-assets.tests.test_processing_scripts.SplitImageAssetsPackageTests.test_prepare_plan_manifest_preserves_existing_scope_selection_on_incremental_update
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add split-image-assets/scripts/prepare_plan_manifest.py split-image-assets/scripts/package_state_lib.py split-image-assets/tests/test_processing_scripts.py
git commit -m "fix: harden scope selection round-trip updates"
```

## Spec Coverage Check

- explicit clear flags: covered by Task 1
- preserve-by-default semantics: covered by Tasks 1 and 2
- no validator semantic change: enforced by scope and by tests staying helper-local
- unresolved multi-family state and incremental update safety: covered by Task 2

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-06-split-image-assets-planning-helper-depth.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
