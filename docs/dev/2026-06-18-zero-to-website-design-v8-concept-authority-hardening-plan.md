# Zero-To-Website Design V8 Concept Authority Hardening Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: concept-generation and authority hardening

## Goal

Harden the generated-image path so `zero-to-website-design` is stricter about when generation is justified and how generated visuals can become authoritative.

After V6 and V7, the package is much better at:

- preferring repo-owned and historical visuals
- documenting `temporary-binding` ownership
- keeping provenance artifacts aligned

The remaining soft spot is the generated-image path itself. The package says generation is not the default first move, but it still leaves too much room for sloppy escalation from "nice concept" to "binding route owner."

This phase should make the generated-image workflow more explicit and harder to misuse.

## Why This Phase

Real projects drift in one of two bad ways:

1. the agent generates fresh images too early even though existing project visuals were already enough
2. a generated concept becomes de facto binding without a clear record of:
   - why generation was needed
   - what route it controls
   - what milestone it supports
   - what stronger source would later replace it

That is exactly the kind of workflow ambiguity this repository has been progressively removing.

## Target Outcome

When generation happens, the package should make it obvious:

- why generation was necessary
- what source paths were considered first
- whether the output is still `exploratory`, `candidate`, `approved-direction`, `binding-route`, or `temporary-binding`
- what route or section the generated image owns
- whether the generated image supports `Framework Ready` or `Visual Delivery Ready`
- what event would retire or replace it

## Scope

In scope:

- harden `zero-to-website-design/references/concept-generation.md`
- update `zero-to-website-design/SKILL.md` and `docs/usage/zero-to-website-design.md` if needed to keep the public workflow aligned
- expand tests that guard the generation authority contract
- update project memory for the new stage

Out of scope:

- changing provenance status names
- adding new templates beyond what already exists
- adding generator-specific scripts
- changing unrelated continuity or review package behavior

## Concrete Gaps To Close

### 1. Generation entry conditions are still too implicit

The package says generation is not the first move, but it does not yet strongly require the agent to record:

- why repo-owned or historical visuals were insufficient
- whether generation is happening because the user explicitly asked for it
- whether the generated image is only for direction, or intended to drive route implementation

### 2. Authority escalation for generated images is under-specified

The package currently describes the status ladder, but it does not strongly encode the conditions that should be true before a generated image is allowed to become:

- `approved-direction`
- `binding-route`
- `temporary-binding`

### 3. Upgrade and retirement triggers for generated images are too light

When a generated route mockup becomes authoritative for a phase, the package should make the replacement rule explicit instead of leaving it implied.

## Proposed Changes

### `references/concept-generation.md`

Strengthen it with:

- a generation-entry checklist
- a "record why generation was needed" rule
- explicit escalation conditions for:
  - `candidate`
  - `approved-direction`
  - `binding-route`
  - `temporary-binding`
- explicit replacement/retirement rules

### `SKILL.md`

Keep the main workflow aligned by making it clearer that:

- explicit user request can justify generation
- generation still does not bypass source-path evaluation
- generated route owners must be recorded with milestone and replacement trigger

### `docs/usage/zero-to-website-design.md`

Add a clearer generated-concept example and note that generation should still record why it was chosen instead of existing visuals.

### Tests

Expand package tests so the repo proves:

- concept-generation guidance includes generation-entry conditions
- generated-image status escalation is documented
- generated authority requires route ownership and replacement tracking
- public docs stay aligned with the stricter contract

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- generated-image entry conditions are explicit
- generated-image authority escalation is explicit
- generated authoritative outputs require route ownership and replacement tracking
- tests lock the stricter contract
- validation passes
- production review passes with no confirmed blocking issue

## Suggested Commit Shape

- `feat(阶段16): harden concept authority`
