# Zero-To-Website Design V21 Public Workflow Alignment Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: public-doc alignment hardening

## Goal

Align the public-facing `zero-to-website-design` summaries with the actual shipped workflow contract so the top-level docs no longer understate the package as a simple brief-to-QA flow.

## Why This Phase

The current shipped package already includes:

- twelve workflow steps, not eleven
- a dedicated long-running project-memory step
- stronger delivery handoff expectations

But the public docs still drift in two places:

- `docs/usage/zero-to-website-design.md` says the skill guides Codex through eleven gates even though the list has twelve numbered steps
- `README.md` still describes `zero-to-website-design` mainly as a brief-to-QA workflow and under-signals memory-aware delivery and handoff continuity

## Target Outcome

After this phase:

- the usage guide names the correct workflow count
- the repository overview describes `zero-to-website-design` as a design-to-QA-to-handoff workflow
- tests lock the public wording in place

## Scope

In scope:

- update `docs/usage/zero-to-website-design.md`
- update `README.md`
- update `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new references
- changes to `SKILL.md` workflow steps
- changes to memory scripts or templates

## Concrete Gaps To Close

### 1. Public workflow count is wrong

The usage guide says "eleven gates" while listing twelve steps. That is an objective drift against the shipped package.

### 2. Repository overview still undersells the latest contract

The README describes `zero-to-website-design` as a brief-to-QA workflow, but the skill now explicitly includes project-memory and handoff continuity.

## Proposed Changes

### `docs/usage/zero-to-website-design.md`

- change the workflow summary to say twelve gates
- keep the current numbered list intact

### `README.md`

- update the short description of `zero-to-website-design` so it includes handoff continuity or memory-aware delivery
- update the "Best fit" bullets if needed to reflect delivery handoff and framework-first workflow

### `zero-to-website-design/tests/test_skill_package.py`

- add assertions that protect the corrected public gate count
- add assertions that the top-level repo overview includes the broader zero-to-website framing

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- no public usage doc claims eleven gates when the listed workflow has twelve steps
- the repo overview no longer undersells the memory-aware handoff aspect of `zero-to-website-design`
- tests lock the wording
- production review passes with no blocking issue

## Decision Record

- Decision: Use public workflow alignment as the V21 stage for `zero-to-website-design`.
- Rationale: This is the clearest remaining contract drift visible from the package entry docs, and fixing it improves trust without widening scope.
- Risk: The README wording could become too verbose.
- Mitigation: Keep the copy compact and only add the missing delivery-memory cues.

## Suggested Commit Shape

- `docs(阶段30): align public workflow summary`
