# Awesome Skills Docs Landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the repository's newcomer documentation so GitHub visitors can choose a skill quickly, install it, and route into deeper docs without scanning a long homepage.

**Architecture:** Keep the repository docs in two layers: a short GitHub landing page and a stable `docs/usage` navigation layer. Rewrite the landing files first, then lightly normalize skill usage intros, and protect the new contract with a repository-level docs test.

**Tech Stack:** Markdown, Python `unittest`, repository-relative link validation

---

### Task 1: Update the repository docs contract test first

**Files:**
- Modify: `tests/test_repository_docs.py`
- Verify against: `README.md`, `docs/usage/quickstart.md`, `docs/usage/skill-matrix.md`, `docs/zh/README.zh-CN.md`

- [ ] **Step 1: Rewrite the failing assertions for the new landing contract**

Replace the current release-heavy assertions with checks for:

- `README.md` linking to `docs/usage/skill-matrix.md`, `docs/usage/quickstart.md`, and `docs/zh/README.zh-CN.md`
- `README.md` containing a `## Choose a Skill` section
- `docs/usage/quickstart.md` describing repository-level install flow instead of `production-code-quality-review`
- `docs/usage/skill-matrix.md` containing the shared fields `When to use`, `Best for`, `Avoid when`, `Typical outputs`, and `Docs`
- `docs/zh/README.zh-CN.md` mirroring the same top-level sections as the English landing

- [ ] **Step 2: Add a lightweight link integrity helper**

In `tests/test_repository_docs.py`, add a helper that extracts repository-relative Markdown links from the rewritten landing files and asserts that each target file exists.

Check at minimum:

- `README.md`
- `docs/usage/quickstart.md`
- `docs/usage/skill-matrix.md`
- `docs/zh/README.zh-CN.md`

- [ ] **Step 3: Run the repository docs test and confirm it fails**

Run:

```bash
python3 -m unittest tests.test_repository_docs -v
```

Expected: FAIL because the current docs still follow the old landing structure.

### Task 2: Rewrite the landing pages

**Files:**
- Modify: `README.md`
- Modify: `docs/usage/quickstart.md`
- Modify: `docs/usage/skill-matrix.md`
- Modify: `docs/zh/README.zh-CN.md`

- [ ] **Step 1: Rewrite `README.md` as the GitHub landing**

Implement these sections in order:

- repository positioning
- choose a skill
- recommended starting points
- install
- docs
- repository layout
- for maintainers

Keep the homepage short. Keep the skill matrix visible near the top. Remove long package-by-package prose and package-specific command sprawl.

- [ ] **Step 2: Rewrite `docs/usage/quickstart.md` as a repository quickstart**

Make the page answer:

- where skills install
- how to install one skill
- how to reload skills
- how to verify discovery
- where to go next for skill selection or troubleshooting

Remove the `production-code-quality-review`-specific walkthrough.

- [ ] **Step 3: Tighten `docs/usage/skill-matrix.md` around the shared decision schema**

Ensure every skill is described with:

- `When to use`
- `Best for`
- `Avoid when`
- `Typical outputs`
- `Docs`

Preserve a compact "pick by problem type" section and minimal routing prompts, but avoid turning the page into a second homepage.

- [ ] **Step 4: Mirror the landing structure in `docs/zh/README.zh-CN.md`**

Use the same seven sections as `README.md`.

Keep:

- skill IDs in English
- commands and paths unchanged
- explicit notes when linked deeper pages are English-only

### Task 3: Lightly sync skill usage entry pages

**Files:**
- Modify: `docs/usage/best-project-memory.md`
- Modify: `docs/usage/evidence-driven-bugfix.md`
- Modify: `docs/usage/little-lighthouse-blog-publisher.md`
- Modify: `docs/usage/split-image-assets.md`
- Modify: `docs/usage/zero-to-website-design.md`

- [ ] **Step 1: Normalize the opening block on each page**

Make each page open with:

- one-sentence purpose
- when to use it
- what it produces
- where to go if the user is still choosing among skills

- [ ] **Step 2: Add or normalize a short related-docs section**

Each synced usage page should point back to:

- `docs/usage/skill-matrix.md`
- `docs/usage/quickstart.md`
- one or two nearby relevant docs

- [ ] **Step 3: Keep substantive package guidance intact**

Do not rewrite the full skill manuals. Only adjust the newcomer-facing top section and obvious navigation drift.

### Task 4: Verify the docs milestone

**Files:**
- Verify: `README.md`
- Verify: `docs/usage/quickstart.md`
- Verify: `docs/usage/skill-matrix.md`
- Verify: `docs/zh/README.zh-CN.md`
- Verify: `tests/test_repository_docs.py`

- [ ] **Step 1: Run the repository docs test**

Run:

```bash
python3 -m unittest tests.test_repository_docs -v
```

Expected: PASS

- [ ] **Step 2: Run the full repository test surface**

Run:

```bash
python3 -m unittest discover tests -v
```

Expected: PASS

- [ ] **Step 3: Manually sanity-check the landing path**

Confirm by reading the docs that:

- `README.md` is shorter and clearly landing-oriented
- the first recommended action is to use the skill matrix
- `quickstart.md` is repository-level
- the Chinese overview follows the same entry structure

- [ ] **Step 4: Prepare the branch for review**

Collect:

- changed file list
- verification results
- remaining non-blocking doc backlog items, if any
