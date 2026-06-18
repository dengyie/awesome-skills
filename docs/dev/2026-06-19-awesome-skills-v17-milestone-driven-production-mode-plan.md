# V17 Milestone-Driven Production Mode Plan

## Milestone

Align `best-project-memory`, `production-code-quality-review`, and `zero-to-website-design` with a milestone-driven production development mode.

## Goal

Make the three skills guide Codex toward one bounded, verifiable delivery loop: define the current milestone, freeze P0/P1 scope, execute a small number of meaningful phases, review each phase with production criteria, commit atomically, summarize, and stop.

## P0/P1 Scope

- P0: Add an explicit milestone execution contract to project-memory guidance so future project work has a finite scope container, P0/P1 priority split, backlog handling, manual-required handling, phase budget, acceptance criteria, and stop conditions.
- P1: Update the review skill so phase-end reviews can report the required categories, quality score, pass state, and blocking/non-blocking routing rules.
- P1: Update the website skill so site builds use the milestone contract instead of expanding into open-ended design and polish loops.
- P1: Add focused regression tests and public usage docs that protect the new behavior.

## Out Of Scope P2/P3

- No new helper scripts for milestone orchestration.
- No broad rewrite of existing skill references.
- No changes to `little-lighthouse-blog-publisher`.
- No EvoMap re-publication in this milestone.
- No repository-wide release-note restructuring.

## Manual Required

- EvoMap credentials and contest resubmission remain external and are not needed for this code/doc milestone.
- Real downstream project validation is outside this repository-only pass.

## Phase Limit

Maximum 3 phases.

## Phase Split

1. Contract design and memory-skill integration.
2. Review and website-skill integration.
3. Regression tests, validation, production review, memory update, and commit.

## Acceptance Criteria

- `best-project-memory/SKILL.md` requires the Step 0 execution contract, P0/P1 scope freeze, P2/P3 backlog routing, manual-required routing, finite phase budget, phase summaries, and stop conditions for milestone-mode project work.
- `production-code-quality-review/SKILL.md` supports phase-end milestone reviews with the required Chinese category labels and clear blocking rules.
- `zero-to-website-design/SKILL.md` treats each website pass as a bounded milestone and prevents automatic expansion into additional milestones.
- Public usage docs mention the milestone-driven production mode for the three submitted skills.
- Package tests and repository docs tests pass.
- Skill validation passes for the three updated skills.
- Production review finds no blocking P0/P1 issue.

## Stop Conditions

Stop when the three-skill milestone contract is implemented, verified, reviewed, committed, and summarized. Do not open a follow-up milestone for helper scripts, EvoMap upload, or broader docs unless the user explicitly asks later.
