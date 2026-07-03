# Split Image Assets Current Baseline

Date: 2026-07-04
Status: Canonical current-state implementation baseline for `split-image-assets`
Design source: `docs/superpowers/split-image-assets/design.md`

## Authority

This file is the current implementation baseline, not a historical checklist.
It remains the single implementation plan for the active `split-image-assets` line.

Use it to answer:

- what the package has already shipped
- which milestone just closed
- what the next bounded milestone should be
- which follow-ups are backlog versus active work

If a new milestone starts, update this file in place instead of creating a new dated plan under `docs/superpowers/specs/` or `docs/superpowers/plans/`.

## Current Baseline

The current package baseline is:

- planning-first workflow
- explicit `plan_manifest.json` planning surface
- extraction/generation route separation
- generated-reconstruction delivery semantics
- decomposed validator architecture
- decomposed test architecture
- generated-route runtime integration for honest pass gating

This means the package is no longer primarily a packaging helper with extraction-adjacent notes. It is now a route-controlled asset workflow with package truth gates.

## Most Recent Closed Milestone

### `generated-route runtime integration V1`

Closed status: complete

What landed:

- generated-only pass paths can validate honestly without requiring extraction-capable `metadata.capability.production_capable=true`
- generated-only pass now depends on `metadata.capability.generation.production_ready=true`
- generated-route confirmation is enforced with object-scoped `metadata.decision_log[]` evidence rather than package-level confirmation alone
- preflight reporting now includes generated-reconstruction gaps in `missing_roles` and `why_it_matters`
- package docs and contracts now describe generated-only pass behavior explicitly

Verification completed:

- `python -m unittest discover split-image-assets\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\split-image-assets`

## Delivered Milestone Ladder

These are the important completed milestones that define the current architecture:

1. contract and QA hardening
2. capability-preflight and confirmation-driven workflow hardening
3. three-layer workflow refactor
4. planning-first generation-routing V1
5. shared package-state consolidation
6. validator decomposition V1
7. test decomposition V1
8. generated-route runtime integration V1

Treat these as delivered baseline, not as active checklist items.

## Active P0/P1 Status

There is no currently open `split-image-assets` code milestone.

Current state:

- no active P0 blocker
- no active P1 implementation branch
- current package baseline is verified and published

Any new work should begin by choosing a new bounded milestone on top of the current baseline instead of implicitly continuing the last one.

## Next Recommended Milestones

Choose only one as the next bounded milestone:

1. deeper generated-route provider support
   - better provider-specific runtime contract depth
   - more explicit provider capability mapping
   - richer generated candidate lifecycle helpers

2. broader fixture and package migration
   - update older generated fixtures that still rely on package-level `generation_routing`
   - migrate hand-authored packages to the current generated-only pass contract

3. planning-helper depth
   - better planning helpers around route scoring, attempt budgeting, and pilot grouping
   - keep this bounded to planning surfaces, not broad validator expansion

## Out Of Scope Until A New Milestone Is Chosen

Do not reopen these lines by default:

- built-in segmentation runtime hosting
- built-in general image-generation runtime hosting
- broad installer UX work
- unbounded docs rewrite beyond authority cleanup
- large refactors unrelated to route truthfulness or package contract maintenance

## Current Doc Ownership

Use this ownership model when changing the package:

- `design.md`
  - why the workflow is shaped this way
  - invariants
  - route and delivery truth model

- `implementation-plan.md`
  - current baseline
  - last closed milestone
  - next milestone candidates

- `split-image-assets/SKILL.md`
  - agent runtime entrypoint
  - practical workflow and output expectations

- `split-image-assets/references/quick-contract.md`
  - fast truth summary

- `split-image-assets/references/asset-package-contract.md`
  - full validator-facing package contract

- `docs/usage/split-image-assets.md`
  - operator guide

## Acceptance Criteria For The Current Baseline

The package should be treated as healthy only when all of the following remain true:

1. package docs, validator rules, and review-writing rules agree on generated-only pass behavior
2. object-scoped generation-routing evidence is enforced for generated-route objects
3. planning-first route control remains the canonical workflow story
4. the validator and tests stay decomposed by domain rather than collapsing back into monoliths
5. verification remains green on the full `split-image-assets` suite and `quick_validate.py`

## Change Policy For The Next Round

When a new milestone starts:

1. rewrite this file to the new active milestone header
2. keep the delivered baseline summary
3. move the prior active milestone into the delivered milestone ladder
4. do not reintroduce long stale checklists for already completed work
