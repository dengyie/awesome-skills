# Evidence-Driven Bugfix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and integrate the new `evidence-driven-bugfix` skill package so `awesome-skills` ships a replacement-grade primary bugfix workflow with evidence-first diagnosis, mandatory failing evidence before implementation, fresh verification before any success claim, and loop-until-fixed behavior with narrow legal exits.

**Architecture:** Add a new standalone skill package under `evidence-driven-bugfix/` with a strict `SKILL.md` orchestrator, reference documents for each gate and contract, and package-level tests that enforce the workflow rules. Then wire the package into repository-level discovery and documentation surfaces so it behaves like the other first-class skill packages.

**Tech Stack:** Markdown skill packages, YAML metadata, Python `unittest`, repository docs in Markdown

---

## File Structure

### New package files

- Create: `evidence-driven-bugfix/SKILL.md`
- Create: `evidence-driven-bugfix/agents/openai.yaml`
- Create: `evidence-driven-bugfix/references/workflow-contract.md`
- Create: `evidence-driven-bugfix/references/symptom-capture.md`
- Create: `evidence-driven-bugfix/references/failing-evidence-gate.md`
- Create: `evidence-driven-bugfix/references/root-cause-investigation.md`
- Create: `evidence-driven-bugfix/references/minimal-fix-plan.md`
- Create: `evidence-driven-bugfix/references/fresh-verification-gate.md`
- Create: `evidence-driven-bugfix/references/truthful-completion.md`
- Create: `evidence-driven-bugfix/references/manual-required-and-external-blockers.md`
- Create: `evidence-driven-bugfix/references/output-contract.md`
- Create: `evidence-driven-bugfix/tests/test_skill_package.py`

### Repository integration files

- Modify: `README.md`
- Modify: `docs/usage/skill-matrix.md`
- Create: `docs/usage/evidence-driven-bugfix.md`
- Modify: `tests/test_repository_docs.py`

### Existing design inputs

- Read: `docs/superpowers/specs/2026-06-20-evidence-driven-bugfix-design.md`
- Read: `production-code-quality-review/SKILL.md`
- Read: `zero-to-website-design/SKILL.md`
- Read: `little-lighthouse-blog-publisher/tests/test_skill_package.py`
- Read: `tests/test_repository_docs.py`

---

### Task 1: Scaffold the skill package contract

**Files:**
- Create: `evidence-driven-bugfix/SKILL.md`
- Create: `evidence-driven-bugfix/agents/openai.yaml`
- Test: `evidence-driven-bugfix/tests/test_skill_package.py`

- [ ] **Step 1: Re-read the approved design spec and extract the non-negotiable contract**

Read:

```text
docs/superpowers/specs/2026-06-20-evidence-driven-bugfix-design.md
```

Write down these must-have package rules before drafting files:

- package name is `evidence-driven-bugfix`
- it is a replacement-grade primary bugfix workflow
- it must encode the three iron laws
- it must define the eight workflow states
- it must define the six gates
- it must continue looping until `Fixed`, `Manual-required`, or `Proven-external-blocker`
- it must forbid success claims without fresh verification evidence

- [ ] **Step 2: Write the failing package-contract test first**

Create `evidence-driven-bugfix/tests/test_skill_package.py` with this initial failing test skeleton:

```python
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class EvidenceDrivenBugfixPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "workflow-contract.md",
            ROOT / "references" / "symptom-capture.md",
            ROOT / "references" / "failing-evidence-gate.md",
            ROOT / "references" / "root-cause-investigation.md",
            ROOT / "references" / "minimal-fix-plan.md",
            ROOT / "references" / "fresh-verification-gate.md",
            ROOT / "references" / "truthful-completion.md",
            ROOT / "references" / "manual-required-and-external-blockers.md",
            ROOT / "references" / "output-contract.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the package test to verify it fails**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
FAIL: test_required_skill_files_are_present
```

because the package files do not exist yet.

- [ ] **Step 4: Write the minimal package entrypoint and metadata**

Create `evidence-driven-bugfix/SKILL.md` with:

- YAML frontmatter
- package name and description
- mission
- three iron laws
- eight states
- six gate summary
- unified loop rule
- legal exits
- reference routing section

Use this skeleton as the starting point:

```markdown
---
name: evidence-driven-bugfix
description: Use when fixing any bug, test failure, or unexpected behavior that requires evidence-first diagnosis, failing evidence before implementation, fresh verification before any success claim, and continued looping until fixed or legally blocked.
---

# Evidence-Driven Bugfix

## Mission

Fix bugs through evidence, not guesses.

Do not implement fixes without failing evidence.
Do not claim success without fresh verification evidence.
Continue the loop until the bug is fixed or an evidence-backed legal exit applies.

## Iron Laws

```text
NO FIX WITHOUT FAILING EVIDENCE
NO ROOT-CAUSE GAP HIDDEN BY A SYMPTOM FIX
NO SUCCESS CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```
```

Create `evidence-driven-bugfix/agents/openai.yaml` with:

```yaml
display_name: "Evidence-Driven Bugfix"
description: "A replacement-grade primary bugfix workflow that enforces evidence-first diagnosis, failing evidence before implementation, and fresh verification before any success claim."
trigger_phrases:
  - "$evidence-driven-bugfix"
```

- [ ] **Step 5: Run the package test again and confirm the file-presence failure narrows**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
FAIL: test_required_skill_files_are_present
```

but now only the reference files should be missing.

- [ ] **Step 6: Commit the scaffold**

```bash
git add evidence-driven-bugfix/SKILL.md evidence-driven-bugfix/agents/openai.yaml evidence-driven-bugfix/tests/test_skill_package.py
git commit -m "feat: scaffold evidence-driven-bugfix package"
```

---

### Task 2: Implement the workflow references

**Files:**
- Create: `evidence-driven-bugfix/references/workflow-contract.md`
- Create: `evidence-driven-bugfix/references/symptom-capture.md`
- Create: `evidence-driven-bugfix/references/failing-evidence-gate.md`
- Create: `evidence-driven-bugfix/references/root-cause-investigation.md`
- Create: `evidence-driven-bugfix/references/minimal-fix-plan.md`
- Create: `evidence-driven-bugfix/references/fresh-verification-gate.md`
- Create: `evidence-driven-bugfix/references/truthful-completion.md`
- Create: `evidence-driven-bugfix/references/manual-required-and-external-blockers.md`
- Create: `evidence-driven-bugfix/references/output-contract.md`
- Test: `evidence-driven-bugfix/tests/test_skill_package.py`

- [ ] **Step 1: Extend the package test so it fails on missing core workflow language**

Add these tests to `evidence-driven-bugfix/tests/test_skill_package.py`:

```python
    def test_skill_frontmatter_and_core_rules_are_present(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: evidence-driven-bugfix", frontmatter)
        self.assertIn("evidence-first diagnosis", frontmatter)
        self.assertIn("NO FIX WITHOUT FAILING EVIDENCE", skill_text)
        self.assertIn("NO ROOT-CAUSE GAP HIDDEN BY A SYMPTOM FIX", skill_text)
        self.assertIn("NO SUCCESS CLAIM WITHOUT FRESH VERIFICATION EVIDENCE", skill_text)
        self.assertIn("Manual-required", skill_text)
        self.assertIn("Proven-external-blocker", skill_text)
```

```python
    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 8)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])
```

- [ ] **Step 2: Run the tests to verify they fail on missing reference content**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
FAIL
```

because the referenced markdown files do not exist yet or are not wired from `SKILL.md`.

- [ ] **Step 3: Write `workflow-contract.md`**

Create `evidence-driven-bugfix/references/workflow-contract.md` covering:

- mission summary
- eight-state state machine
- six-gate sequence
- unified loop rule
- legal exits
- explicit prohibition on silent completion claims

Include this exact terminal-outcome section:

```markdown
## Terminal Outcomes

Only these outcomes may end the loop:

- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

Anything else returns the workflow to investigation, evidence gathering, or root-cause analysis.
```

- [ ] **Step 4: Write the gate-specific references**

Create each file with one focused responsibility:

- `symptom-capture.md`
- `failing-evidence-gate.md`
- `root-cause-investigation.md`
- `minimal-fix-plan.md`
- `fresh-verification-gate.md`
- `truthful-completion.md`
- `manual-required-and-external-blockers.md`
- `output-contract.md`

Each file must:

- define its purpose
- list required inputs/observations
- list prohibited shortcuts
- define the pass condition

For `truthful-completion.md`, include this explicit forbidden-language section:

```markdown
## Forbidden Completion Language

Do not say:

- "should be fixed"
- "probably solved"
- "looks good"
- "done"

unless fresh verification evidence has already proven the original failure is gone.
```

- [ ] **Step 5: Update `SKILL.md` so it routes to the references explicitly**

Add a `Reference Routing` section that cites all reference files with concrete trigger rules such as:

```markdown
- Read `references/failing-evidence-gate.md` before any implementation starts.
- Read `references/root-cause-investigation.md` when the failure origin is unclear or the stack is deep.
- Read `references/fresh-verification-gate.md` before making any status or success claim.
- Read `references/truthful-completion.md` before reporting completion, pause state, or blocker state.
```

- [ ] **Step 6: Run the package tests and verify they pass**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
OK
```

- [ ] **Step 7: Commit the workflow references**

```bash
git add evidence-driven-bugfix/references evidence-driven-bugfix/SKILL.md evidence-driven-bugfix/tests/test_skill_package.py
git commit -m "feat: add evidence-driven-bugfix workflow references"
```

---

### Task 3: Tighten the skill entrypoint into a true workflow driver

**Files:**
- Modify: `evidence-driven-bugfix/SKILL.md`
- Test: `evidence-driven-bugfix/tests/test_skill_package.py`

- [ ] **Step 1: Write the failing behavior-contract test**

Add this test to `evidence-driven-bugfix/tests/test_skill_package.py`:

```python
    def test_skill_entrypoint_defines_states_gates_and_looping(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for expected in [
            "Investigating",
            "Reproduced",
            "Root-caused",
            "Fixing",
            "Verifying",
            "Fixed",
            "Manual-required",
            "Proven-external-blocker",
            "Symptom Capture",
            "Failing Evidence Gate",
            "Root Cause Investigation",
            "Minimal Fix Plan",
            "Fresh Verification Gate",
            "Truthful Completion Gate",
        ]:
            self.assertIn(expected, skill_text)

        self.assertIn("continue the loop until the bug is fixed", skill_text)
        self.assertIn("No failing evidence means no implementation", skill_text)
        self.assertIn("If fresh verification fails, return to investigation", skill_text)
```

- [ ] **Step 2: Run the tests to verify the new contract fails**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
FAIL: test_skill_entrypoint_defines_states_gates_and_looping
```

until the exact workflow language is added.

- [ ] **Step 3: Rewrite `SKILL.md` to be a workflow orchestrator, not a reference page**

Ensure `SKILL.md` contains these sections in order:

- mission
- iron laws
- state machine
- six gate summary
- loop rule
- legal exits
- reference routing
- output expectations

Add these exact or near-exact lines:

```markdown
No failing evidence means no implementation.
```

```markdown
If fresh verification fails, return to investigation or root-cause analysis and continue the loop.
```

```markdown
Do not imply success, completion, or correctness without fresh verification evidence.
```

- [ ] **Step 4: Re-run the package tests and verify green**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
```

Expected:

```text
OK
```

- [ ] **Step 5: Commit the orchestrator hardening**

```bash
git add evidence-driven-bugfix/SKILL.md evidence-driven-bugfix/tests/test_skill_package.py
git commit -m "feat: harden evidence-driven-bugfix entrypoint"
```

---

### Task 4: Add repository-level documentation and discovery

**Files:**
- Modify: `README.md`
- Create: `docs/usage/evidence-driven-bugfix.md`
- Modify: `docs/usage/skill-matrix.md`
- Test: `tests/test_repository_docs.py`

- [ ] **Step 1: Write the failing repository-docs test first**

Extend `tests/test_repository_docs.py` with assertions for the new package:

```python
        self.assertIn("`evidence-driven-bugfix`", readme)
        self.assertIn("Evidence-Driven Bugfix", readme)
        self.assertIn("docs/usage/evidence-driven-bugfix.md", readme)
        self.assertIn("`evidence-driven-bugfix`", skill_matrix)
        self.assertIn("docs/usage/evidence-driven-bugfix.md", skill_matrix)
```

Add an assertion that the root README install section includes:

```python
        self.assertIn("cp -R evidence-driven-bugfix ~/.agents/skills/", readme)
```

- [ ] **Step 2: Run the docs test and confirm failure**

Run:

```bash
python3 -m unittest tests.test_repository_docs -v
```

Expected:

```text
FAIL
```

because the new skill is not documented yet.

- [ ] **Step 3: Update `README.md`**

Add `evidence-driven-bugfix` consistently to:

- the "currently ships" list
- the included skills section
- the repo layout section
- the install copy commands
- the documentation index
- local verification commands if you want package tests explicitly surfaced

Use wording aligned with the design:

```markdown
`evidence-driven-bugfix`: primary bugfix workflow that requires failing evidence before implementation, fresh verification before any success claim, and continued looping until fixed or legally blocked
```

- [ ] **Step 4: Write `docs/usage/evidence-driven-bugfix.md`**

Create a focused user guide with:

- what the skill is for
- when to use it
- the six gates in short form
- examples of acceptable failing evidence
- examples of allowed outcomes:
  - `Fixed`
  - `Manual-required`
  - `Proven-external-blocker`
- examples of forbidden phrases
- a short prompt example such as:

```text
Use $evidence-driven-bugfix to fix this failure by first capturing logs, getting stable failing evidence, tracing the root cause, applying the minimal fix, and only reporting success after fresh verification.
```

- [ ] **Step 5: Update `docs/usage/skill-matrix.md`**

Add one new skill row with columns matching the current matrix:

- Skill
- Best when you need
- Core outputs
- Common pairings
- Avoid when

Recommended content:

- best when you need: a disciplined bugfix workflow that prevents guess-fixes and false completion claims
- core outputs: failing evidence, root cause, minimal fix, fresh verification result, truthful status
- common pairings: `best-project-memory`, `production-code-quality-review`
- avoid when: the user only wants a high-level review, not bugfix execution

Also add:

- a dedicated "Use `evidence-driven-bugfix` first when..." routing section
- a fast routing prompt

- [ ] **Step 6: Re-run the repository docs test and verify green**

Run:

```bash
python3 -m unittest tests.test_repository_docs -v
```

Expected:

```text
OK
```

- [ ] **Step 7: Commit repository integration docs**

```bash
git add README.md docs/usage/evidence-driven-bugfix.md docs/usage/skill-matrix.md tests/test_repository_docs.py
git commit -m "docs: integrate evidence-driven-bugfix into repo surfaces"
```

---

### Task 5: Final package verification and polish

**Files:**
- Modify: `evidence-driven-bugfix/SKILL.md`
- Modify: `evidence-driven-bugfix/tests/test_skill_package.py`
- Modify: `README.md`
- Modify: `docs/usage/evidence-driven-bugfix.md`
- Modify: `docs/usage/skill-matrix.md`
- Modify: `tests/test_repository_docs.py`

- [ ] **Step 1: Run the full relevant verification bundle**

Run:

```bash
python3 -m unittest discover evidence-driven-bugfix/tests -v
python3 -m unittest tests.test_repository_docs -v
```

Expected:

```text
OK
OK
```

- [ ] **Step 2: Re-read the design spec line by line and map every requirement to the implementation**

Check:

- package name matches
- no `scripts/` directory was added in v1
- all references exist
- three iron laws are present
- six gates are present
- legal exits are present
- looping rule is explicit
- docs explain the skill consistently

If anything is missing, patch it now before continuing.

- [ ] **Step 3: Do a placeholder and ambiguity scan**

Run:

```bash
rg -n "TBD|TODO|placeholder|to be decided|maybe|probably" evidence-driven-bugfix README.md docs/usage/evidence-driven-bugfix.md docs/usage/skill-matrix.md
```

Expected:

```text
Only intentional examples such as forbidden-language examples may appear.
```

If accidental placeholders or weak wording appear, remove them.

- [ ] **Step 4: Check git diff for contract drift**

Run:

```bash
git diff -- evidence-driven-bugfix README.md docs/usage/evidence-driven-bugfix.md docs/usage/skill-matrix.md tests/test_repository_docs.py
```

Verify manually:

- no accidental scope expansion
- no references to scripts that do not exist
- no contradictions between `SKILL.md` and the usage docs

- [ ] **Step 5: Commit the final polish**

```bash
git add evidence-driven-bugfix README.md docs/usage/evidence-driven-bugfix.md docs/usage/skill-matrix.md tests/test_repository_docs.py
git commit -m "test: verify evidence-driven-bugfix package contract"
```

---

## Spec Coverage Check

- Package name and role: covered in Tasks 1-3
- Iron laws: covered in Tasks 1-3
- Eight-state workflow: covered in Task 3
- Six gates: covered in Tasks 2-3
- Unified loop rule: covered in Task 3
- Legal exits: covered in Tasks 2-3
- No scripts in v1: preserved by file structure and Task 5 review
- Repository integration: covered in Task 4
- Package tests: covered in Tasks 1-3 and Task 5

## Placeholder Scan

Intentional placeholders that remain acceptable in this plan:

- none

## Type and Naming Consistency Check

Canonical names used throughout this plan:

- package: `evidence-driven-bugfix`
- legal exits: `Fixed`, `Manual-required`, `Proven-external-blocker`
- six gates:
  - `Symptom Capture`
  - `Failing Evidence Gate`
  - `Root Cause Investigation`
  - `Minimal Fix Plan`
  - `Fresh Verification Gate`
  - `Truthful Completion Gate`

## Recommended Execution Strategy

Use subagent-driven execution if possible. The tasks are naturally separable:

1. scaffold package
2. build references
3. harden entrypoint
4. wire repository docs
5. run final verification and polish
