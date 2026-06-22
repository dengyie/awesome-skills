# Split Image Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `split-image-assets` as the sixth public skill, with workflow docs, deterministic asset-package scripts, tests, and repository navigation updates.

**Architecture:** The skill separates visual judgment from deterministic packaging. Codex/AI/manual tools produce or evaluate cutouts, masks, and repaired backgrounds; bundled Python scripts initialize packages, compose previews, and validate structure and metadata.

**Tech Stack:** Markdown skill docs, Python standard library, Pillow for image preview generation, `unittest` for tests, `skill-creator` quick validation.

---

## File Structure

- Create `split-image-assets/SKILL.md`: skill trigger, mission, workflow, reference routing, script usage, output expectations.
- Create `split-image-assets/agents/openai.yaml`: UI metadata.
- Create `split-image-assets/references/workflow.md`: detailed production workflow.
- Create `split-image-assets/references/asset-package-contract.md`: package layout and metadata contract.
- Create `split-image-assets/references/qa-standards.md`: asset usability and inspection standards.
- Create `split-image-assets/references/manual-review.md`: manual takeover branch and uncertainty rules.
- Create `split-image-assets/scripts/init_asset_package.py`: initialize package directories and starter files.
- Create `split-image-assets/scripts/build_previews.py`: generate deterministic white, checkerboard, overview, and 2x2 previews from existing PNG assets.
- Create `split-image-assets/scripts/validate_asset_package.py`: validate package structure, metadata, alpha channels, masks, previews, QA status, and manual-review flags.
- Create `split-image-assets/tests/test_skill_package.py`: package, docs, script, and tiny fixture tests.
- Create `docs/usage/split-image-assets.md`: user-facing usage guide.
- Modify `README.md`: list the sixth skill, install command, package section, verification command, docs link, repo layout, release-note scope.
- Modify `docs/usage/skill-matrix.md`: add routing rows and prompts.
- Modify `docs/releases/README.md`: add split-image-assets to non-versioned package coverage.
- Modify `docs/zh/README.zh-CN.md`: update count and add split-image-assets references without rewriting unrelated mojibake text.
- Modify `docs/zh/releases/README.zh-CN.md`: add split-image-assets to non-versioned package coverage.
- Modify `tests/test_repository_docs.py`: assert repository docs expose the sixth skill.
- Modify `.codex-memory/*`: record this milestone and completion state after implementation and verification.

## Task 1: Package Skeleton And Contract Tests

**Files:**
- Create: `split-image-assets/tests/test_skill_package.py`
- Create: `split-image-assets/SKILL.md`
- Create: `split-image-assets/agents/openai.yaml`
- Create: `split-image-assets/references/workflow.md`
- Create: `split-image-assets/references/asset-package-contract.md`
- Create: `split-image-assets/references/qa-standards.md`
- Create: `split-image-assets/references/manual-review.md`

- [ ] **Step 1: Write package tests**

Create `split-image-assets/tests/test_skill_package.py` with tests that check required files, frontmatter, reference links, usage docs, and script names:

```python
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent


class SplitImageAssetsPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "workflow.md",
            ROOT / "references" / "asset-package-contract.md",
            ROOT / "references" / "qa-standards.md",
            ROOT / "references" / "manual-review.md",
            ROOT / "scripts" / "init_asset_package.py",
            ROOT / "scripts" / "build_previews.py",
            ROOT / "scripts" / "validate_asset_package.py",
            REPO / "docs" / "usage" / "split-image-assets.md",
        ]

        missing = [str(path.relative_to(REPO)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_core_rules_are_present(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: split-image-assets", frontmatter)
        self.assertIn("asset package", frontmatter)
        self.assertIn("ANALYZE BEFORE EXTRACTING", skill_text)
        self.assertIn("REUSABLE ASSETS BEFORE PREVIEWS", skill_text)
        self.assertIn("NEVER HIDE UNCERTAINTY", skill_text)
        self.assertIn("2x2 sprite sheet is only a preview", skill_text)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 4)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_usage_doc_mentions_contract_previews_metadata_qa_and_manual_review(self):
        usage = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "asset package",
            "transparent PNG",
            "mask",
            "background_clean.png",
            "metadata.json",
            "qa_report.md",
            "sprite_sheet_2x2.png",
            "manual review",
            "does not perform segmentation",
        ]:
            self.assertIn(expected, usage)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and confirm they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover split-image-assets\tests -v
```

Expected: FAIL because the package files do not exist yet.

- [ ] **Step 3: Create `SKILL.md` and reference files**

Create `split-image-assets/SKILL.md` with concise workflow instructions and reference routing. Include these exact safety rules:

```text
ANALYZE BEFORE EXTRACTING
REUSABLE ASSETS BEFORE PREVIEWS
TRANSPARENT PNGS ARE PRODUCTION ASSETS
PREVIEWS ARE INSPECTION ARTIFACTS
NEVER HIDE UNCERTAINTY
```

Create the four reference files with the contracts from `docs/superpowers/specs/2026-06-23-split-image-assets-design.md`.

- [ ] **Step 4: Create `agents/openai.yaml`**

Create:

```yaml
display_name: "Split Image Assets"
description: "A production asset-splitting workflow for turning source images into reusable transparent PNG layers, masks, cleaned backgrounds, metadata, previews, and QA evidence."
trigger_phrases:
  - "$split-image-assets"
```

- [ ] **Step 5: Run package tests**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover split-image-assets\tests -v
```

Expected: package file tests that do not depend on scripts should pass once docs and placeholders exist; script-related tests may still fail until Task 2.

## Task 2: Asset Package Initialization Script

**Files:**
- Create: `split-image-assets/scripts/init_asset_package.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add tests for package initialization**

Extend `test_skill_package.py` with a temp-directory test that creates a tiny PNG, runs the init script, and asserts standard outputs:

```python
import json
import subprocess
import sys
import tempfile
from PIL import Image


    def test_init_asset_package_creates_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_asset_package.py"),
                    str(source),
                    str(output),
                    "--package-name",
                    "fixture",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "source" / "source_original.png").exists())
            self.assertTrue((output / "assets").is_dir())
            self.assertTrue((output / "masks").is_dir())
            self.assertTrue((output / "previews").is_dir())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["package_name"], "fixture")
            self.assertEqual(metadata["source"]["width"], 4)
            self.assertEqual(metadata["source"]["height"], 3)
            self.assertEqual(metadata["qa"]["status"], "needs-review")
            self.assertIn("Final status: needs-review", (output / "qa_report.md").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run test and confirm it fails**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_init_asset_package_creates_standard_layout -v
```

Expected: FAIL because `init_asset_package.py` is not implemented.

- [ ] **Step 3: Implement init script**

Implement `init_asset_package.py` with `argparse`, `pathlib`, `shutil.copy2`, and Pillow for source dimensions. Use JSON indentation and UTF-8 writing. Refuse to overwrite an existing `metadata.json` unless `--force` is passed.

- [ ] **Step 4: Run init test**

Run the same unittest command.

Expected: PASS.

## Task 3: Preview Builder Script

**Files:**
- Create: `split-image-assets/scripts/build_previews.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add preview tests**

Add a test that initializes a package, writes `assets/main_object_transparent.png`, writes an object entry to metadata, runs `build_previews.py`, and asserts:

- `previews/main_object_whitebg.png` exists
- `previews/main_object_checkerboard.png` exists
- `previews/overview_decomposition.png` exists
- `previews/sprite_sheet_2x2.png` exists

- [ ] **Step 2: Run test and confirm it fails**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_build_previews_creates_inspection_images -v
```

Expected: FAIL because `build_previews.py` is not implemented.

- [ ] **Step 3: Implement preview builder**

Implement Pillow helpers:

- `make_checkerboard(size, cell=8)`
- `composite_on_background(image, background)`
- `load_object_assets(metadata, package_dir)`
- `build_individual_previews(...)`
- `build_overview(...)`
- `build_sprite_sheet(...)`

The script must read object entries from `metadata.json` and must not invent segmentation. It only uses existing transparent PNG paths.

- [ ] **Step 4: Run preview test**

Run the same unittest command.

Expected: PASS.

## Task 4: Package Validator Script

**Files:**
- Create: `split-image-assets/scripts/validate_asset_package.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add validator tests**

Add one passing fixture test and one failing fixture test:

- passing: initialized package with source, one RGBA transparent object, one source-sized mask, preview files, metadata final status, and QA report
- failing: object PNG saved as RGB without alpha should fail with text mentioning `alpha`

- [ ] **Step 2: Run tests and confirm they fail**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_accepts_complete_fixture split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_object_without_alpha -v
```

Expected: FAIL because `validate_asset_package.py` is not implemented.

- [ ] **Step 3: Implement validator**

Implement validation with actionable error messages and nonzero exit for failures. Required checks:

- top-level `source/`, `assets/`, `masks/`, `previews/`, `metadata.json`, `qa_report.md`
- metadata has `schema_version`, `package_name`, `source`, `objects`, `qa`
- source backup exists
- object asset paths exist
- object assets with role `main`, `secondary`, `group`, or `shadow` use PNG with alpha
- mask paths exist and match source dimensions when `coordinate_space` is `source`
- preview paths listed in metadata exist
- `qa_report.md` contains `Final status:`
- `low` confidence or `ai-assisted` extraction has at least one manual-review flag

- [ ] **Step 4: Run validator tests**

Run the same unittest command.

Expected: PASS.

## Task 5: Usage Docs And Repository Navigation

**Files:**
- Create: `docs/usage/split-image-assets.md`
- Modify: `README.md`
- Modify: `docs/usage/skill-matrix.md`
- Modify: `docs/releases/README.md`
- Modify: `docs/zh/README.zh-CN.md`
- Modify: `docs/zh/releases/README.zh-CN.md`
- Modify: `tests/test_repository_docs.py`

- [ ] **Step 1: Update repository docs test first**

Add assertions for:

- `split-image-assets` appears in `README.md`
- `Split Image Assets` appears in `README.md`
- `docs/usage/split-image-assets.md` appears in README, skill matrix, releases docs, and Chinese docs
- install command includes `cp -R split-image-assets ~/.agents/skills/`
- verification command includes `python3 -m unittest discover split-image-assets/tests -v`
- docs describe six shipped skills

- [ ] **Step 2: Run repository docs test and confirm it fails**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover tests -v
```

Expected: FAIL because navigation has not been updated.

- [ ] **Step 3: Write usage guide**

Create `docs/usage/split-image-assets.md` with sections:

- Purpose
- When to use
- Output package
- Workflow
- Commands
- QA statuses
- Manual review
- Limitations

State clearly that the deterministic scripts do not perform segmentation.

- [ ] **Step 4: Update English navigation docs**

Update README, skill matrix, and releases README to list six skills and include the new usage link, install command, and verification command.

- [ ] **Step 5: Update Chinese navigation docs carefully**

Update only the count, bullet, links, and non-versioned package list in `docs/zh/README.zh-CN.md` and `docs/zh/releases/README.zh-CN.md`. Do not rewrite unrelated existing mojibake text in this task.

- [ ] **Step 6: Run repository docs tests**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover tests -v
```

Expected: PASS.

## Task 6: Skill Validation, Full Tests, Memory, And Commit

**Files:**
- Modify: `.codex-memory/project-state.md`
- Modify: `.codex-memory/session-log.md`
- Modify: `.codex-memory/decisions.md`
- Modify: `.codex-memory/todo.md`

- [ ] **Step 1: Run package tests**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover split-image-assets\tests -v
```

Expected: PASS.

- [ ] **Step 2: Run skill quick validation**

Run:

```powershell
$env:PYTHONUTF8='1'; python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets
```

Expected: PASS.

- [ ] **Step 3: Run repository docs tests**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover tests -v
```

Expected: PASS.

- [ ] **Step 4: Run all skill package tests**

Run:

```powershell
$env:PYTHONUTF8='1'; python -m unittest discover best-project-memory\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover evidence-driven-bugfix\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover little-lighthouse-blog-publisher\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover production-code-quality-review\tests -v
$env:PYTHONUTF8='1'; python -m unittest discover zero-to-website-design\tests -v
```

Expected: PASS.

- [ ] **Step 5: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 6: Update project memory**

Record:

- new sixth public skill
- decision to separate deterministic packaging scripts from segmentation
- verification commands and outcomes
- remaining limitations around external/manual segmentation

- [ ] **Step 7: Commit implementation**

Run:

```powershell
git status --short --branch --untracked-files=all
git add -- split-image-assets docs/usage/split-image-assets.md README.md docs/usage/skill-matrix.md docs/releases/README.md docs/zh/README.zh-CN.md docs/zh/releases/README.zh-CN.md tests/test_repository_docs.py .codex-memory
git commit -m "Add split image assets skill"
```

Expected: commit succeeds with all implementation files staged.

