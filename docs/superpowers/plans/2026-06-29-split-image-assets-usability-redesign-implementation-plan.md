# Split Image Assets Usability Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `split-image-assets` into an agent-first, conservative-continuous workflow where progress stays in commentary, only hard stop events or medium/high-risk semantic divergence may exit the workflow, and every allowed stop follows a recommendation-and-impact handoff contract.

**Architecture:** Keep the redesign local to `split-image-assets`. First freeze the new stop/continue contract into tests and top-level docs. Then rewrite the workflow and confirmation references so the state machine and gate taxonomy become executable documentation instead of loose prose. Finish by aligning any remaining contract-facing docs/tests and running a bounded phase-gate review before stopping.

**Tech Stack:** Markdown skill docs, Python standard library tests, `unittest`, `rg`, `git`

---

## File Structure

- Modify `split-image-assets/SKILL.md`: make the conservative continuous execution model, five-state machine, event taxonomy, and stop contract explicit at the skill entrypoint.
- Modify `split-image-assets/references/workflow.md`: convert the workflow into a continue-versus-stop runbook with stage-level state and pause rules.
- Modify `split-image-assets/references/confirmation-prompts.md`: restrict prompts to allowed stop classes and require `grill-me`-style recommendation/impact framing.
- Modify `split-image-assets/references/asset-package-contract.md`: clarify that `decision_log` / `confirmation` are formal-state surfaces only and keep object-scoped semantic divergence evidence explicit.
- Modify `docs/usage/split-image-assets.md`: add a short agent-facing happy path and a stop-versus-continue quick table.
- Modify `split-image-assets/tests/test_skill_package.py`: add regression tests for doc contract presence, allowed stop classes, anti-pattern exclusions, and example wording expectations.

### Task 1: Freeze The Stop/Continue Contract In Tests And Entry Docs

**Files:**
- Modify: `split-image-assets/tests/test_skill_package.py`
- Modify: `split-image-assets/SKILL.md`
- Modify: `docs/usage/split-image-assets.md`

- [ ] **Step 1: Add failing tests for the new execution model language**

```python
def test_skill_frontmatter_and_core_rules_are_present(self):
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("PROGRESS UPDATES ARE COMMENTARY, NOT CONFIRMATION GATES", skill_text)
    self.assertIn("ONLY THREE EVENT TYPES MAY PAUSE EXECUTION", skill_text)
    self.assertIn("Running", skill_text)
    self.assertIn("AwaitingDecision", skill_text)
    self.assertIn("AwaitingExternalBlocker", skill_text)
    self.assertIn("AwaitingApproval", skill_text)


def test_usage_doc_mentions_conservative_continuous_execution(self):
    usage_text = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(encoding="utf-8")
    self.assertIn("default execution model", usage_text.lower())
    self.assertIn("continue versus stop", usage_text.lower())
    self.assertIn("progress updates are commentary", usage_text.lower())
```

- [ ] **Step 2: Run the new doc tests and verify RED**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_skill_frontmatter_and_core_rules_are_present
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_mentions_conservative_continuous_execution
```

Expected: at least one failure because the current docs do not yet fully encode the approved agent-first stop/continue model.

- [ ] **Step 3: Rewrite the top of `split-image-assets/SKILL.md` around the new contract**

```md
At the top-level skill entrypoint, make these ideas explicit:
- conservative continuous execution is the default
- progress updates are commentary only
- only hard stop events or medium/high-risk semantic divergence may exit the workflow
- every exit must include:
  - Why This Needs a Human
  - Recommendation
  - Options and Impact
  - What I Will Do After Confirmation
```

- [ ] **Step 4: Add the short usage-level stop/continue entry section**

```md
In `docs/usage/split-image-assets.md`, add:
- a "Default Execution Model" section
- a two-column quick table for "Continue" versus "Stop"
- one anti-example showing a progress-only pause that should not happen
- one positive example of a correct semantic-divergence stop with a recommendation
```

- [ ] **Step 5: Re-run the doc tests and verify GREEN**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_skill_frontmatter_and_core_rules_are_present
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_mentions_conservative_continuous_execution
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1 atomically**

```bash
git add split-image-assets/SKILL.md docs/usage/split-image-assets.md split-image-assets/tests/test_skill_package.py
git commit -m "feat(phase-1): define split-image-assets stop-continue contract"
```

### Task 2: Reclassify Workflow Stages And Prompt Templates Around The State Machine

**Files:**
- Modify: `split-image-assets/references/workflow.md`
- Modify: `split-image-assets/references/confirmation-prompts.md`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add failing tests for workflow taxonomy coverage**

```python
def test_workflow_doc_maps_gate_taxonomy_to_states(self):
    workflow_text = (ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
    self.assertIn("tooling_preflight", workflow_text)
    self.assertIn("granularity_alignment", workflow_text)
    self.assertIn("pilot_object", workflow_text)
    self.assertIn("approximate_reconstruction", workflow_text)
    self.assertIn("final_acceptance", workflow_text)
    self.assertIn("candidate_promotion", workflow_text)
    self.assertIn("AwaitingDecision", workflow_text)
    self.assertIn("AwaitingExternalBlocker", workflow_text)
    self.assertIn("AwaitingApproval", workflow_text)


def test_confirmation_prompts_are_limited_to_allowed_stop_classes(self):
    prompt_text = (ROOT / "references" / "confirmation-prompts.md").read_text(encoding="utf-8")
    self.assertIn("Why This Needs a Human", prompt_text)
    self.assertIn("Recommendation", prompt_text)
    self.assertIn("Options and Impact", prompt_text)
    self.assertIn("What I Will Do After Confirmation", prompt_text)
    self.assertIn("must not be used for progress-only pauses", prompt_text.lower())
```

- [ ] **Step 2: Run the workflow/prompt tests and verify RED**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_workflow_doc_maps_gate_taxonomy_to_states
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_confirmation_prompts_are_limited_to_allowed_stop_classes
```

Expected: FAIL because the current references are still more narrative than state-machine driven.

- [ ] **Step 3: Rewrite `references/workflow.md` as a continue-versus-stop runbook**

```md
For each major stage, explicitly include:
- default state
- whether pause is allowed
- the allowed pause category when pause is allowed
- the minimum evidence needed before a stop
- the reason it continues when pause is not allowed

Reclassify these gate names directly in the file:
- tooling_preflight
- granularity_alignment
- pilot_object
- approximate_reconstruction
- final_acceptance
- candidate_promotion
```

- [ ] **Step 4: Rewrite `references/confirmation-prompts.md` into an allowed-stop template library**

```md
For each retained prompt, include:
- event class
- state
- stop condition
- recommended answer style
- effect on metadata

Explicitly remove or forbid:
- progress-only pauses
- stage-complete pauses
- multiple unrelated questions in one stop
- asks that are already resolved by prior user instructions
```

- [ ] **Step 5: Re-run the workflow/prompt tests and verify GREEN**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_workflow_doc_maps_gate_taxonomy_to_states
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_confirmation_prompts_are_limited_to_allowed_stop_classes
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2 atomically**

```bash
git add split-image-assets/references/workflow.md split-image-assets/references/confirmation-prompts.md split-image-assets/tests/test_skill_package.py
git commit -m "feat(phase-2): reclassify split-image-assets workflow stops"
```

### Task 3: Align Formal Contract Docs And Guard Against Drift

**Files:**
- Modify: `split-image-assets/references/asset-package-contract.md`
- Modify: `docs/usage/split-image-assets.md`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add failing tests for formal-surface wording and object-scoped evidence guidance**

```python
def test_asset_package_contract_separates_formal_state_from_commentary(self):
    contract_text = (ROOT / "references" / "asset-package-contract.md").read_text(encoding="utf-8")
    self.assertIn("decision_log", contract_text)
    self.assertIn("formal state", contract_text.lower())
    self.assertIn("must not contain", contract_text.lower())
    self.assertIn("progress updates", contract_text.lower())
    self.assertIn("object-scoped", contract_text.lower())


def test_usage_doc_includes_allowed_stop_examples(self):
    usage_text = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(encoding="utf-8")
    self.assertIn("external blocker", usage_text.lower())
    self.assertIn("semantic divergence", usage_text.lower())
    self.assertIn("formal approval", usage_text.lower())
```

- [ ] **Step 2: Run the contract/usage tests and verify RED**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_asset_package_contract_separates_formal_state_from_commentary
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_includes_allowed_stop_examples
```

Expected: FAIL because the contract/usage wording is not yet fully aligned with the approved usability redesign.

- [ ] **Step 3: Clarify `asset-package-contract.md` around formal-state surfaces**

```md
Add explicit language that:
- `decision_log` and `confirmation` are formal-state surfaces only
- commentary, progress notes, and routine status updates must stay out of them
- object-specific semantic divergence should remain object-scoped in evidence and confirmation records
```

- [ ] **Step 4: Finalize the usage guide with stop examples and anti-examples**

```md
Add short examples for:
- a true external blocker stop
- a correct semantic-divergence stop
- a correct final-approval stop
- a progress-only anti-example that should remain commentary
```

- [ ] **Step 5: Re-run the contract/usage tests and verify GREEN**

Run:

```bash
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_asset_package_contract_separates_formal_state_from_commentary
python3 -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_includes_allowed_stop_examples
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3 atomically**

```bash
git add split-image-assets/references/asset-package-contract.md docs/usage/split-image-assets.md split-image-assets/tests/test_skill_package.py
git commit -m "feat(phase-3): align split-image-assets formal-state docs"
```

### Task 4: Full Regression, Phase-Gate Review, And Milestone Close

**Files:**
- Modify only if required by blocking review findings discovered in this task.

- [ ] **Step 1: Run the full `split-image-assets` regression suite**

Run:

```bash
python3 split-image-assets/tests/test_skill_package.py -v
```

Expected: all package tests pass.

- [ ] **Step 2: Run a bounded production quality review for this milestone**

Review the milestone increment using `production-code-quality-review` in phase-gate mode over:

```text
split-image-assets/SKILL.md
split-image-assets/references/workflow.md
split-image-assets/references/confirmation-prompts.md
split-image-assets/references/asset-package-contract.md
docs/usage/split-image-assets.md
split-image-assets/tests/test_skill_package.py
```

Report in this structure:

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

- [ ] **Step 3: Fix only P0/P1 blockers if the review fails**

If the review reports blocking issues:

```bash
# fix only the blocking files
python3 split-image-assets/tests/test_skill_package.py -v
```

Do not widen scope into new UX work.

- [ ] **Step 4: Commit any review-driven blocking fixes**

```bash
git add split-image-assets docs/usage/split-image-assets.md
git commit -m "fix(phase-4): close split-image-assets usability review blockers"
```

- [ ] **Step 5: Stop after the milestone closes**

When the regression suite passes and the phase-gate review is `通过` or `有条件通过`, stop and report:

```text
✅ 阶段 4 完成
Milestone：Split Image Assets Usability Redesign
完成内容：Agent-first stop/continue contract, workflow reclassification, prompt library rewrite, formal-state doc alignment, regression coverage
验证结果：Full split-image-assets package test suite passes
审查评分：use the actual phase-gate review score from Step 2
通过状态：use the actual phase-gate review decision from Step 2
关键决策：Only hard events and medium/high-risk semantic divergence may exit the workflow
Backlog 新增：list only concrete non-blocking follow-up ideas actually discovered during execution
Manual-required：None
剩余阶段预算：0
```

## Self-Review

- Spec coverage: the plan maps directly to the usability redesign spec's main sections: default execution model, five-state machine, event taxonomy, gate reclassification, doc information architecture, formal-state alignment, and test strategy.
- Placeholder scan: no `TODO`, `TBD`, or “figure it out later” steps remain.
- Type consistency: the plan consistently uses `Running`, `AwaitingDecision`, `AwaitingExternalBlocker`, `AwaitingApproval`, `Completed`, `decision_log`, `confirmation`, and “medium/high-risk semantic divergence” across tasks.
