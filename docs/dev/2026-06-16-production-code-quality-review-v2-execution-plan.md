# Production Code Quality Review V2 Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve user onboarding and convenience for `production-code-quality-review` without changing its production-review philosophy.

**Architecture:** Add documentation and scripts around the existing deterministic core, extend the review brief CLI with more presentation modes, and reduce entrypoint verbosity in `SKILL.md`.

**Tech Stack:** Markdown, Python standard library, shell scripts, unittest

---

### Task 1: Add tests for new CLI output modes

**Files:**
- Modify: `production-code-quality-review/tests/test_collect_review_context_cli.py`

- [ ] **Step 1: Add a compact output expectation for `review-entrypoint.py`**
- [ ] **Step 2: Add a JSON-mode expectation if needed for parity**
- [ ] **Step 3: Run tests to confirm failures before implementation**

### Task 2: Implement new CLI modes and local helper scripts

**Files:**
- Modify: `production-code-quality-review/scripts/review-entrypoint.py`
- Modify: `production-code-quality-review/scripts/review_skill_lib.py`
- Create: `production-code-quality-review/scripts/install-local-skill.sh`
- Create: `production-code-quality-review/scripts/update-local-skill.sh`

- [ ] **Step 1: Add `compact` output mode**
- [ ] **Step 2: Keep markdown and JSON behavior intact**
- [ ] **Step 3: Add install helper**
- [ ] **Step 4: Add update helper**
- [ ] **Step 5: Re-run tests and fix any regressions**

### Task 3: Improve onboarding docs and tighten `SKILL.md`

**Files:**
- Create: `docs/usage/golden-path.md`
- Modify: `README.md`
- Modify: `production-code-quality-review/SKILL.md`

- [ ] **Step 1: Write the shortest recommended path from install to real review**
- [ ] **Step 2: Link it prominently from the README**
- [ ] **Step 3: Compress `SKILL.md` by removing repeated explanation while preserving workflow clarity**

### Task 4: Verify V2

**Files:**
- Modify if needed: newly added scripts or docs

- [ ] **Step 1: Run the full test suite**
- [ ] **Step 2: Exercise the new CLI mode manually**
- [ ] **Step 3: Check helper scripts for path correctness**
