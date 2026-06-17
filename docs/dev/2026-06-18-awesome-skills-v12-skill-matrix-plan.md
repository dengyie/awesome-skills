# Awesome Skills V12 Skill Matrix Plan

> Status: Implemented in working tree
> Target surface: repository-level usage documentation
> Phase type: public navigation hardening

## Goal

Add a dedicated repository-level skill matrix so a reader can quickly decide which shipped skill to use before diving into package-specific docs.

After V11, the repository-level release docs are more accurate, but the public usage surface still lacks a compact "which skill fits which task" reference. Existing pages like `quickstart.md`, `golden-path.md`, and `examples.md` remain centered on `production-code-quality-review`.

## Why This Phase

The current documentation has a navigation gap:

- `README.md` says the repo ships three skills
- package usage docs explain each skill in isolation
- release docs now describe the scope correctly
- there is still no dedicated top-level matrix that compares the three shipped skills side by side

That makes it harder for a new user to answer a simple question: "Which skill should I reach for first?"

## Target Outcome

After this phase:

- the repo has a dedicated top-level skill matrix page
- readers can compare the three shipped skills by problem type, outputs, and best-fit tasks
- README and Chinese overview can route to the matrix as the main repository-level chooser
- tests protect the existence and key wording of the new matrix

## Scope

In scope:

- add a repository-level usage doc for the skill matrix
- align `README.md` and `docs/zh/README.zh-CN.md` to point to it
- add light regression coverage for the new navigation contract
- update project memory for the new stage

Out of scope:

- changing skill package behavior
- rewriting package-specific quickstarts
- creating full Chinese translations for every usage doc in this phase

## Concrete Gaps To Close

### 1. No dedicated "choose the right skill" page exists

Users currently infer this from README prose or package-specific docs.

### 2. Current public entry docs skew toward the review package

`quickstart.md`, `golden-path.md`, and `examples.md` mostly describe `production-code-quality-review`, which is fine for that package but not enough as repository-level navigation.

### 3. The repo needs one compact comparison artifact

A single matrix can summarize:

- when to use each skill
- what artifacts each skill produces
- when skills are commonly used together

## Proposed Changes

### `docs/usage/skill-matrix.md`

Add a dedicated matrix that covers:

- `best-project-memory`
- `production-code-quality-review`
- `zero-to-website-design`

Include:

- primary use case
- best triggers
- core outputs
- common pairings
- when not to use each skill

### `README.md`

Route readers to the matrix from the main documentation list.

### `docs/zh/README.zh-CN.md`

Add a Chinese pointer that tells readers the matrix is the primary repository-level skill chooser.

### Tests

Extend repository-level docs regression coverage so the matrix page and README links are protected.

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\tests -v`
- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- a dedicated repository-level skill matrix page exists
- README and Chinese overview route readers to it
- tests protect the navigation contract
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use a dedicated top-level skill matrix as V12 instead of another release-summary-only pass.
- Rationale: The remaining public-doc gap is skill selection, not release scope. A matrix has more user value than another prose-only release summary.
- Risk: The page could become a shallow restatement of README content.
- Mitigation: Keep it comparative and decision-oriented, not just descriptive.

## Suggested Commit Shape

- `docs(阶段20): add skill matrix`
