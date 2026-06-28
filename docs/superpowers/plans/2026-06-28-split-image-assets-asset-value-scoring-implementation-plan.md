# Split Image Assets Asset Value Scoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an editability-first asset value scoring layer to `split-image-assets` so ordinary text-like content defaults to downstream rebuild instead of raster extraction, while fidelity-critical and ambiguous text-like content remain auditable and enforceable.

**Architecture:** Keep the change local to `split-image-assets`. First freeze the scoring and routing contract into docs, package schema, and fixture expectations. Then harden the validator and review tooling so illegal text/action combinations cannot pass. Finish by expanding regression coverage, running phase-gate review, and stopping after the milestone closes.

**Tech Stack:** Markdown skill docs, Python standard library scripts, `unittest`, `rg`, `git`

---

## File Structure

- Modify `split-image-assets/SKILL.md`: add the asset value scoring policy, text-like routing rules, and `requires_user_confirmation` trigger semantics.
- Modify `split-image-assets/references/workflow.md`: insert the `Asset Value Scoring Gate` before extraction and describe the object routing sequence.
- Modify `split-image-assets/references/confirmation-prompts.md`: add the text-like ambiguity confirmation prompt and a “do not ask for ordinary text defaults” rule.
- Modify `split-image-assets/references/asset-package-contract.md`: add object-level scoring, routing, rebuild intent, and text semantics fields.
- Modify `docs/usage/split-image-assets.md`: explain user-facing text-handling behavior.
- Modify `split-image-assets/scripts/init_asset_package.py`: seed the new object metadata defaults where package-owned object templates are initialized.
- Modify `split-image-assets/scripts/record_quality_review.py`: support writing scoring/routing metadata and confirmation outcomes without hand-editing JSON.
- Modify `split-image-assets/scripts/validate_asset_package.py`: enforce legal text/action combinations and required confirmation evidence.
- Modify `split-image-assets/tests/test_skill_package.py`: add regression tests for ordinary text rebuild routing, fidelity-critical text extraction, ambiguous text confirmation, and validator failures.

### Task 1: Freeze The Scoring And Routing Contract

**Files:**
- Modify: `split-image-assets/SKILL.md`
- Modify: `split-image-assets/references/workflow.md`
- Modify: `split-image-assets/references/confirmation-prompts.md`
- Modify: `split-image-assets/references/asset-package-contract.md`
- Modify: `docs/usage/split-image-assets.md`
- Test: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add doc expectations to the package tests**

```python
def test_skill_docs_describe_asset_value_scoring_and_text_routing(self):
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    workflow_text = (ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
    contract_text = (ROOT / "references" / "asset-package-contract.md").read_text(encoding="utf-8")

    self.assertIn("Asset Value Scoring Gate", skill_text)
    self.assertIn("ordinary text", skill_text.lower())
    self.assertIn("rebuild_downstream", workflow_text)
    self.assertIn("text_role", contract_text)
    self.assertIn("recommended_action", contract_text)
```

- [ ] **Step 2: Run the new doc expectation test and verify RED**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_skill_docs_describe_asset_value_scoring_and_text_routing`
Expected: FAIL because the current docs do not yet mention the new scoring contract.

- [ ] **Step 3: Update `split-image-assets/SKILL.md` with the scoring policy**

```md
Add a new section after the interaction/gating guidance that states:
- asset value scoring happens before extraction
- ordinary text, button labels, numeric values, and form values default to `rebuild_downstream`
- logo wordmarks, decorative text, and fidelity-critical text may route to `extract_asset`
- ambiguous high-complexity text-like objects route to `requires_user_confirmation`
```

- [ ] **Step 4: Update `split-image-assets/references/workflow.md` with the new gate order**

```md
Insert `Asset Value Scoring Gate` between `semantic split plan` and extraction.
Document the routing flow:
1. classify text-like vs non-text
2. assign `text_role` / `text_render_class`
3. compute `editability_score`, `visual_complexity_score`, `asset_value_score`
4. set `recommended_action`
5. resolve `final_action`
6. extract only when `final_action=extract_asset`
```

- [ ] **Step 5: Update `split-image-assets/references/confirmation-prompts.md` with the ambiguity prompt**

```md
Add a prompt template:
"Should this text-like object be rebuilt downstream as editable content, or preserved as a visual asset for fidelity?"

Also add a rule stating that ordinary text defaults must not pause execution.
```

- [ ] **Step 6: Update `split-image-assets/references/asset-package-contract.md` and `docs/usage/split-image-assets.md`**

```md
Contract additions per object:
- `value_scoring.editability_score`
- `value_scoring.visual_complexity_score`
- `value_scoring.asset_value_score`
- `value_scoring.scoring_reason`
- `decision_routing.recommended_action`
- `decision_routing.final_action`
- `decision_routing.decision_source`
- `rebuild_intent.rebuildable_downstream`
- `rebuild_intent.rebuild_notes`
- `text_semantics.text_role`
- `text_semantics.text_render_class`
```

- [ ] **Step 7: Re-run the doc expectation test and the existing packaging doc tests**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_skill_docs_describe_asset_value_scoring_and_text_routing split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_mentions_contract_previews_metadata_qa_and_manual_review`
Expected: PASS.

- [ ] **Step 8: Commit Phase 1 changes**

```bash
git add split-image-assets/SKILL.md split-image-assets/references/workflow.md split-image-assets/references/confirmation-prompts.md split-image-assets/references/asset-package-contract.md docs/usage/split-image-assets.md split-image-assets/tests/test_skill_package.py
git commit -m "feat(phase-1): define asset value scoring contract"
```

### Task 2: Make The Scoring Contract Executable In Metadata And Review Tooling

**Files:**
- Modify: `split-image-assets/scripts/init_asset_package.py`
- Modify: `split-image-assets/scripts/record_quality_review.py`
- Test: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add failing metadata-default tests for new object fields**

```python
def test_init_asset_package_object_schema_supports_value_scoring_fields(self):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        source = tmp_path / "source.png"
        Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
        output = tmp_path / "package"
        init_result = self._run_init(source, output)
        self.assertEqual(init_result.returncode, 0, init_result.stderr)
        Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")

        metadata = self._write_single_object_metadata(output)
        obj = metadata["objects"][0]
        self.assertIn("value_scoring", obj)
        self.assertIn("decision_routing", obj)
        self.assertIn("rebuild_intent", obj)
        self.assertIn("text_semantics", obj)
```

- [ ] **Step 2: Run the new metadata-default test and verify RED**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_init_asset_package_object_schema_supports_value_scoring_fields`
Expected: FAIL because the current object template does not include these fields.

- [ ] **Step 3: Extend `split-image-assets/scripts/init_asset_package.py` with schema defaults**

```python
"value_scoring": {
    "editability_score": "unset",
    "visual_complexity_score": "unset",
    "asset_value_score": "unset",
    "scoring_reason": "",
},
"decision_routing": {
    "recommended_action": "unset",
    "final_action": "unset",
    "decision_source": "unset",
},
"rebuild_intent": {
    "rebuildable_downstream": False,
    "rebuild_notes": "",
},
"text_semantics": {
    "text_role": "non-text",
    "text_render_class": "non-text",
},
```

- [ ] **Step 4: Add failing `record_quality_review.py` tests for scoring/routing updates**

```python
def test_record_quality_review_records_text_routing_metadata(self):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        source = tmp_path / "source.png"
        Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
        output = tmp_path / "package"
        init_result = self._run_init(source, output)
        self.assertEqual(init_result.returncode, 0, init_result.stderr)
        Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
        self._write_single_object_metadata(output)

        result = subprocess.run([
            sys.executable,
            str(ROOT / "scripts" / "record_quality_review.py"),
            str(output),
            "--object-id", "main_object",
            "--text-role", "plain-text",
            "--text-render-class", "editable",
            "--editability-score", "high",
            "--visual-complexity-score", "low",
            "--asset-value-score", "low",
            "--scoring-reason", "Ordinary editable text.",
            "--recommended-action", "rebuild_downstream",
            "--final-action", "rebuild_downstream",
            "--routing-decision-source", "explicit-user-confirmed",
            "--rebuildable-downstream", "true",
            "--rebuild-notes", "Do not export a raster asset.",
        ], text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
        obj = metadata["objects"][0]
        self.assertEqual(obj["text_semantics"]["text_role"], "plain-text")
        self.assertEqual(obj["decision_routing"]["final_action"], "rebuild_downstream")
        self.assertTrue(obj["rebuild_intent"]["rebuildable_downstream"])
```

- [ ] **Step 5: Run the new routing test and verify RED**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_records_text_routing_metadata`
Expected: FAIL because the CLI does not yet support the new routing fields.

- [ ] **Step 6: Extend `split-image-assets/scripts/record_quality_review.py` with new CLI args and object updates**

```python
parser.add_argument("--text-role", choices=sorted(ALLOWED_TEXT_ROLES))
parser.add_argument("--text-render-class", choices=sorted(ALLOWED_TEXT_RENDER_CLASSES))
parser.add_argument("--editability-score", choices=sorted(ALLOWED_SCORE_VALUES))
parser.add_argument("--visual-complexity-score", choices=sorted(ALLOWED_SCORE_VALUES))
parser.add_argument("--asset-value-score", choices=sorted(ALLOWED_SCORE_VALUES))
parser.add_argument("--scoring-reason")
parser.add_argument("--recommended-action", choices=sorted(ALLOWED_ROUTING_ACTIONS))
parser.add_argument("--final-action", choices=sorted(ALLOWED_ROUTING_ACTIONS))
parser.add_argument("--routing-decision-source", choices=sorted(ALLOWED_ROUTING_DECISION_SOURCES))
parser.add_argument("--rebuildable-downstream", choices=["true", "false"])
parser.add_argument("--rebuild-notes")
```

- [ ] **Step 7: Re-run the metadata/routing tests and verify GREEN**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_init_asset_package_object_schema_supports_value_scoring_fields split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_records_text_routing_metadata`
Expected: PASS.

- [ ] **Step 8: Commit Phase 2 write-path changes**

```bash
git add split-image-assets/scripts/init_asset_package.py split-image-assets/scripts/record_quality_review.py split-image-assets/tests/test_skill_package.py
git commit -m "feat(phase-2): record asset value scoring metadata"
```

### Task 3: Enforce Text Routing In Validation And Regression Tests

**Files:**
- Modify: `split-image-assets/scripts/validate_asset_package.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add failing validator tests for ordinary text, fidelity-critical text, and ambiguous text-like routes**

```python
def test_validate_asset_package_rejects_plain_text_extract_asset_without_override(self):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        source = tmp_path / "source.png"
        Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
        output = tmp_path / "package"
        init_result = self._run_init(source, output)
        self.assertEqual(init_result.returncode, 0, init_result.stderr)
        Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
        metadata = self._write_single_object_metadata(output)
        metadata["objects"][0]["text_semantics"] = {
            "text_role": "plain-text",
            "text_render_class": "editable",
        }
        metadata["objects"][0]["value_scoring"] = {
            "editability_score": "high",
            "visual_complexity_score": "low",
            "asset_value_score": "low",
            "scoring_reason": "Ordinary UI label.",
        }
        metadata["objects"][0]["decision_routing"] = {
            "recommended_action": "rebuild_downstream",
            "final_action": "extract_asset",
            "decision_source": "explicit-user-confirmed",
        }

def test_validate_asset_package_accepts_logo_wordmark_extract_asset(self):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        source = tmp_path / "source.png"
        Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
        output = tmp_path / "package"
        init_result = self._run_init(source, output)
        self.assertEqual(init_result.returncode, 0, init_result.stderr)
        Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
        metadata = self._write_single_object_metadata(output)
        metadata["objects"][0]["text_semantics"] = {
            "text_role": "logo-wordmark",
            "text_render_class": "visual-fidelity-critical",
        }
        metadata["objects"][0]["value_scoring"] = {
            "editability_score": "low",
            "visual_complexity_score": "high",
            "asset_value_score": "high",
            "scoring_reason": "Brand wordmark with custom letterforms.",
        }
        metadata["objects"][0]["decision_routing"] = {
            "recommended_action": "extract_asset",
            "final_action": "extract_asset",
            "decision_source": "explicit-user-confirmed",
        }

def test_validate_asset_package_rejects_requires_user_confirmation_without_decision_log(self):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        source = tmp_path / "source.png"
        Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
        output = tmp_path / "package"
        init_result = self._run_init(source, output)
        self.assertEqual(init_result.returncode, 0, init_result.stderr)
        Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
        metadata = self._write_single_object_metadata(output)
        metadata["objects"][0]["text_semantics"] = {
            "text_role": "decorative-text",
            "text_render_class": "styled-editable",
        }
        metadata["objects"][0]["value_scoring"] = {
            "editability_score": "medium",
            "visual_complexity_score": "high",
            "asset_value_score": "medium",
            "scoring_reason": "Stylized heading with ambiguous preservation needs.",
        }
        metadata["objects"][0]["decision_routing"] = {
            "recommended_action": "requires_user_confirmation",
            "final_action": "extract_asset",
            "decision_source": "explicit-user-confirmed",
        }
```

- [ ] **Step 2: Run the validator route tests and verify RED**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_plain_text_extract_asset_without_override split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_requires_user_confirmation_without_decision_log`
Expected: FAIL because the validator does not yet enforce these rules.

- [ ] **Step 3: Add new validator enums and field checks**

```python
ALLOWED_TEXT_ROLES = {
    "plain-text", "button-label", "numeric-value", "form-value",
    "logo-wordmark", "decorative-text", "non-text",
}
ALLOWED_TEXT_RENDER_CLASSES = {
    "editable", "styled-editable", "visual-fidelity-critical", "non-text",
}
ALLOWED_SCORE_VALUES = {"unset", "low", "medium", "high"}
ALLOWED_ROUTING_ACTIONS = {
    "unset", "extract_asset", "rebuild_downstream", "requires_user_confirmation", "support_only",
}
```

- [ ] **Step 4: Enforce object-level routing consistency in `validate_asset_package.py`**

```python
if text_role in {"plain-text", "button-label", "numeric-value", "form-value"} and final_action == "extract_asset":
    if text_render_class != "visual-fidelity-critical" and not has_confirmation_override:
        errors.append(f"{object_id}: ordinary editable text-like content must not default to extract_asset")

if recommended_action == "requires_user_confirmation" and not has_confirmation_override:
    errors.append(f"{object_id}: requires_user_confirmation must be resolved through a formal decision record")

if final_action == "rebuild_downstream" and asset_class == "atomic" and reuse_status == "production-ready":
    errors.append(f"{object_id}: rebuild_downstream cannot publish a production raster asset")
```

- [ ] **Step 5: Add positive tests for legal routes**

```python
def test_validate_asset_package_accepts_plain_text_rebuild_downstream(self):
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("Package valid", result.stdout)

def test_validate_asset_package_accepts_visual_fidelity_critical_wordmark_extract_asset(self):
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("Package valid", result.stdout)

def test_validate_asset_package_accepts_confirmed_ambiguous_text_route(self):
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("Package valid", result.stdout)
```

- [ ] **Step 6: Run targeted validator tests and verify GREEN**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_accepts_plain_text_rebuild_downstream split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_accepts_visual_fidelity_critical_wordmark_extract_asset split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_accepts_confirmed_ambiguous_text_route`
Expected: PASS.

- [ ] **Step 7: Run the full package regression suite**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package -v`
Expected: all tests pass.

- [ ] **Step 8: Commit Phase 3 enforcement changes**

```bash
git add split-image-assets/scripts/validate_asset_package.py split-image-assets/tests/test_skill_package.py
git commit -m "fix(phase-3): enforce asset value routing rules"
```

### Task 4: Phase-Gate Review, Fix Loop, And Delivery

**Files:**
- Modify: any files from Tasks 1-3 only if review finds a blocking issue

- [ ] **Step 1: Run the milestone verification commands**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package -v`
Expected: full package suite passes with zero failures.

- [ ] **Step 2: Run production review for the phase increment**

Run: `python3 /Users/mango/.agents/skills/production-code-quality-review/scripts/collect-review-context.py --repo /Users/mango/.config/superpowers/worktrees/dengyie-awesome-skills/feat-split-image-assets-interaction-framework`
Expected: review scope and changed files collected for phase-gate review.

- [ ] **Step 3: Inspect the phase increment and write the phase-gate review**

```text
严重问题：
中等问题：
非阻塞建议：
安全风险：
稳定性风险：
可维护性风险：
测试覆盖：
质量评分：
通过状态：通过 / 有条件通过 / 不通过
```

- [ ] **Step 4: If review finds P0/P1 blockers, fix only those blockers**

Run: `python3 -m unittest split-image-assets.tests.test_skill_package -v`
Expected: tests return to green after each blocker fix.

- [ ] **Step 5: Commit any blocker-only follow-up changes**

```bash
git add split-image-assets/SKILL.md split-image-assets/references/workflow.md split-image-assets/references/confirmation-prompts.md split-image-assets/references/asset-package-contract.md docs/usage/split-image-assets.md split-image-assets/scripts/init_asset_package.py split-image-assets/scripts/record_quality_review.py split-image-assets/scripts/validate_asset_package.py split-image-assets/tests/test_skill_package.py
git commit -m "fix(phase-4): resolve phase-gate blockers"
```

- [ ] **Step 6: Stop after the milestone summary**

```text
# 项目交付总结

Milestone：
完成的 P0/P1：
未执行 Backlog：
Manual-required：
关键决策：
测试与验证：
代码审查结果：
Git 提交：
交付状态：✅ 可交付 / ⚠️ 有条件可交付 / ❌ 不可交付
后续建议：
```

## Self-Review

- Spec coverage: Tasks 1-4 cover scoring docs, metadata schema, review tooling, validator rules, regression tests, and phase-gate review.
- Placeholder scan: no `TODO`/`TBD` placeholders remain in the executable steps.
- Type consistency: the plan uses `value_scoring`, `decision_routing`, `rebuild_intent`, `text_semantics`, `recommended_action`, `final_action`, `text_role`, and `text_render_class` consistently across docs, scripts, validator, and tests.
