# Production Code Quality Review Productization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `production-code-quality-review` feel like a user-facing product by improving first-use documentation and README navigation without changing core behavior.

**Architecture:** Keep the skill package and deterministic scripts unchanged. Add a dedicated `docs/usage/` layer for onboarding and examples, then slim `README.md` into a clean landing page that routes users to the right docs.

**Tech Stack:** Markdown, existing repo layout

---

### Task 1: Add usage docs

**Files:**
- Create: `docs/usage/quickstart.md`
- Create: `docs/usage/review-workflows.md`
- Create: `docs/usage/examples.md`
- Create: `docs/usage/faq.md`

- [ ] **Step 1: Write quickstart for install plus first commands**
- [ ] **Step 2: Write workflow guide for common review scenarios**
- [ ] **Step 3: Add example commands and representative output snippets**
- [ ] **Step 4: Add FAQ for predictable onboarding questions**

### Task 2: Restructure README into homepage plus navigation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Keep the value proposition concise**
- [ ] **Step 2: Keep install and the two main entrypoints visible**
- [ ] **Step 3: Add links to the new usage docs**

### Task 3: Verify documentation quality

**Files:**
- Modify if needed: `README.md`
- Modify if needed: `docs/usage/*.md`

- [ ] **Step 1: Read the docs tree as a first-time user would**
- [ ] **Step 2: Confirm paths and commands match the actual repo**
- [ ] **Step 3: Run a final repo status check**
