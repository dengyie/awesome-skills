# Split Image Assets Interaction Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `split-image-assets` so only three event classes may pause execution, progress updates stay in commentary, and formal gate metadata/tooling/tests all enforce the same interaction contract.

**Architecture:** Keep the change local to the `split-image-assets` package. First lock the intended behavior in tests and skill docs, then harden the write path in `record_quality_review.py`, then make `validate_asset_package.py` reject any state that violates the new gate, source, evidence, or promotion rules.

**Tech Stack:** Markdown skill docs, Python standard library scripts, `unittest`, `rg`, `git worktree`

---

## File Structure

- Modify `split-image-assets/SKILL.md`: declare the interaction iron rules, pause state machine, gate taxonomy, and commentary-vs-gate separation.
- Modify `split-image-assets/references/workflow.md`: align workflow stages and gate ordering with the new pause model.
- Modify `split-image-assets/references/confirmation-prompts.md`: annotate prompts with pause categories and must-ask vs may-infer behavior.
- Modify `split-image-assets/references/asset-package-contract.md`: formalize the stricter `decision_log` and `confirmation` schemas.
- Modify `split-image-assets/scripts/record_quality_review.py`: reject illegal formal gate writes and separate commentary writes from gate writes.
- Modify `split-image-assets/scripts/validate_asset_package.py`: enforce source, evidence, pause category, blocking, and candidate-promotion validity.
- Modify `split-image-assets/tests/test_skill_package.py`: add regression tests for the interaction framework contract and the two scripts.
- Modify `docs/usage/split-image-assets.md`: explain pause behavior to users in plain language.

### Task 1: Freeze The Contract In Tests And Docs

**Files:**
- Modify: `split-image-assets/tests/test_skill_package.py`
- Modify: `split-image-assets/SKILL.md`
- Modify: `split-image-assets/references/workflow.md`
- Modify: `split-image-assets/references/confirmation-prompts.md`
- Modify: `split-image-assets/references/asset-package-contract.md`
- Modify: `docs/usage/split-image-assets.md`

- [ ] **Step 1: Write failing tests for the new interaction contract**

Add tests covering:

```python
def test_record_quality_review_rejects_formal_gate_without_source(self): ...
def test_record_quality_review_rejects_inferred_formal_gate_without_evidence(self): ...
def test_record_quality_review_records_candidate_promotion_gate(self): ...
def test_validate_asset_package_rejects_agent_defaulted_formal_gate(self): ...
def test_validate_asset_package_requires_evidence_for_inferred_confirmation(self): ...
def test_validate_asset_package_requires_candidate_promotion_for_promoted_revision(self): ...
def test_validate_asset_package_rejects_progress_notes_in_decision_log_shape(self): ...
```

- [ ] **Step 2: Run targeted tests and verify RED**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_rejects_formal_gate_without_source
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_requires_candidate_promotion_for_promoted_revision
```

Expected: failures proving the current code still allows loose gate metadata.

- [ ] **Step 3: Update the docs and contract to match the approved spec**

Make the docs explicitly state:

```text
PROGRESS UPDATES ARE COMMENTARY, NOT CONFIRMATION GATES
ONLY THREE EVENT TYPES MAY PAUSE EXECUTION
NO FORMAL GATE MAY BE SATISFIED BY AGENT DEFAULTING
INFERRED-FROM-USER MEANS EVIDENCE-BACKED USER INTENT, NOT AGENT GUESSING
```

Also add `candidate_promotion` to the formal gate set and replace `user_answer` with `recorded_answer` in the contract.

- [ ] **Step 4: Re-run the doc/package tests**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_skill_frontmatter_and_core_rules_are_present
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_usage_doc_mentions_contract_previews_metadata_qa_and_manual_review
```

Expected: GREEN for the updated wording expectations while the script tests still fail.

### Task 2: Harden Formal Gate Writes

**Files:**
- Modify: `split-image-assets/scripts/record_quality_review.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Extend the failing script tests**

Add concrete CLI tests for:

```python
--decision-stage final-acceptance
--confirmation-key candidate_promotion
--decision-source inferred-from-user
--evidence-ref prior-chat:granularity-approved
--pause-category formal-approval
--blocking true
```

Include negative cases for missing `--decision-source`, missing `--pause-category`, illegal `agent-defaulted`, and inferred-without-evidence.

- [ ] **Step 2: Run the targeted CLI tests and verify RED**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_rejects_inferred_formal_gate_without_evidence
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_records_candidate_promotion_gate
```

- [ ] **Step 3: Implement the minimal write-path refactor**

Refactor `record_quality_review.py` to:

```python
FORMAL_PAUSE_CATEGORIES = {"user-decision", "external-blocker", "formal-approval"}
FORMAL_GATE_SOURCES = {"explicit-user-confirmed", "inferred-from-user"}
FORMAL_CONFIRMATION_KEYS = {
    "tooling_preflight",
    "granularity_alignment",
    "pilot_object",
    "approximate_reconstruction",
    "final_acceptance",
    "candidate_promotion",
}
```

Add helpers that:
- detect formal gate writes
- require source and pause category
- require `blocking` on decision-log gate writes
- require `evidence_ref` for inferred writes
- prevent commentary-only invocations from mutating `decision_log` or `confirmation`

- [ ] **Step 4: Re-run targeted script tests and verify GREEN**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_rejects_formal_gate_without_source
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_record_quality_review_records_candidate_promotion_gate
```

### Task 3: Enforce The Contract In Validation And Finish The Milestone

**Files:**
- Modify: `split-image-assets/scripts/validate_asset_package.py`
- Modify: `split-image-assets/tests/test_skill_package.py`

- [ ] **Step 1: Add validator RED tests for the new state machine rules**

Add tests for:
- `agent-defaulted` rejected in formal confirmations and formal decision log entries
- `inferred-from-user` without `evidence_ref` rejected
- `pause_category` outside the 3-value taxonomy rejected
- `candidate_promotion` required when `selected_candidate_id` or promoted revision metadata is present
- downstream `qa.status=pass` blocked when required approval gates are still pending or blocking

- [ ] **Step 2: Run validator tests and verify RED**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_rejects_agent_defaulted_formal_gate
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_requires_evidence_for_inferred_confirmation
python -m unittest split-image-assets.tests.test_skill_package.SplitImageAssetsPackageTests.test_validate_asset_package_requires_candidate_promotion_for_promoted_revision
```

- [ ] **Step 3: Implement validator enforcement**

Update `validate_asset_package.py` so it:
- removes `agent-defaulted` from legal formal gate sources
- requires `evidence_ref` for inferred decision or confirmation entries
- validates `pause_category`, `blocking`, and `recorded_answer`
- requires `candidate_promotion` in the confirmation registry where promotion metadata exists
- keeps commentary outside the formal gate surfaces

- [ ] **Step 4: Run the package regression set**

Run:

```bash
python -m unittest split-image-assets.tests.test_skill_package -v
```

Expected: the `split-image-assets` package test suite passes.

- [ ] **Step 5: Run production review and fix only blocking findings**

Review the changed files with `production-code-quality-review`. If it finds P0/P1 blockers, fix them and rerun the affected tests. Do not widen scope.

- [ ] **Step 6: Commit the milestone atomically**

Run:

```bash
git add split-image-assets docs/usage/split-image-assets.md docs/superpowers/plans/2026-06-28-split-image-assets-interaction-framework.md
git commit -m "feat: refactor split-image-assets interaction framework"
```

## Self-Review

- Spec coverage: all approved requirements map to Task 1-3, including commentary separation, evidence-backed inference, and `candidate_promotion`.
- Placeholder scan: no `TODO`/`TBD` placeholders remain.
- Type consistency: the plan uses `recorded_answer`, `pause_category`, `blocking`, `evidence_ref`, and `candidate_promotion` consistently across docs, tests, write path, and validator.
