# Production Code Quality Review Simplification Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the skill structure for maintainability while preserving the deterministic review workflow.

**Architecture:** Keep the scripts and tests intact as the core execution path, merge related references into fewer files, remove low-value prompt-file sprawl, and tighten `SKILL.md` plus `README.md` to the two main entrypoints.

**Tech Stack:** Markdown, Python standard library, unittest, git

---

### Task 1: Lock simplification behavior with failing tests

**Files:**
- Modify: `production-code-quality-review/tests/test_review_skill_lib.py`
- Modify: `production-code-quality-review/tests/test_collect_review_context_cli.py`

- [ ] **Step 1: Add expectations for merged references and removed reviewer prompts**

- [ ] **Step 2: Run tests to verify the new expectations fail**

Run: `python3 -m unittest discover production-code-quality-review/tests -v`
Expected: FAIL because the old reference names and agent layout still exist

### Task 2: Merge references and update routing

**Files:**
- Create: `production-code-quality-review/references/backend-and-integrations.md`
- Create: `production-code-quality-review/references/verification-and-operations.md`
- Delete: `production-code-quality-review/references/node-api.md`
- Delete: `production-code-quality-review/references/api-integrations.md`
- Delete: `production-code-quality-review/references/observability.md`
- Delete: `production-code-quality-review/references/testing.md`
- Delete: `production-code-quality-review/references/python.md`
- Delete: `production-code-quality-review/references/docker.md`
- Modify: `production-code-quality-review/SKILL.md`
- Modify: `production-code-quality-review/scripts/review_skill_lib.py`

- [ ] **Step 1: Merge backend and API guidance into one reference**
- [ ] **Step 2: Merge testing and observability guidance into one reference**
- [ ] **Step 3: Fold Python and Docker guidance into `review-framework.md` or broader references**
- [ ] **Step 4: Update suggested reference routing to the smaller set**
- [ ] **Step 5: Run tests and fix routing until green**

### Task 3: Remove reviewer prompt sprawl

**Files:**
- Delete: `production-code-quality-review/agents/reviewers/architecture.md`
- Delete: `production-code-quality-review/agents/reviewers/correctness.md`
- Delete: `production-code-quality-review/agents/reviewers/reliability.md`
- Delete: `production-code-quality-review/agents/reviewers/security.md`
- Delete: `production-code-quality-review/agents/reviewers/tests.md`
- Modify: `production-code-quality-review/SKILL.md`

- [ ] **Step 1: Remove reviewer file references**
- [ ] **Step 2: Keep specialist review as conceptual lenses inside `SKILL.md`**
- [ ] **Step 3: Run tests to ensure no behavior regression**

### Task 4: Tighten docs and final verification

**Files:**
- Modify: `README.md`
- Modify: `docs/dev/2026-06-16-production-code-quality-review-redesign.md`

- [ ] **Step 1: Document the simplified shape and the two primary entrypoints**
- [ ] **Step 2: Run fresh verification**

Run:
`python3 -m unittest discover production-code-quality-review/tests -v`

Run:
`python3 production-code-quality-review/scripts/collect-review-context.py --repo .`

Run:
`python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown`

Expected: PASS and usable output
