# Zero-To-Website Design V11 Pre-Code Document Gate Hardening Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: intake-and-doc-gate hardening

## Goal

Tighten the package's pre-code workflow so another session cannot skip from a vague brief or image set straight into broad implementation without first recording the intake output, design-doc baseline, and implementation map.

The package already enforces stronger visual provenance, route readiness, QA evidence, and delivery templates.

The remaining weak spot is earlier in the chain: the intake brief, design-system docs, and implementation-map references still leave too much room for "I'll document it after I code."

## Why This Phase

`zero-to-website-design` is supposed to be a disciplined website-delivery workflow, not only a nice set of later-stage QA rules.

Right now, the package already says:

- write design docs before code
- map routes and components before editing
- document visual authority and delivery state

But the intake and pre-code references do not yet make the artifact gate explicit enough. A downstream user could still:

- ask a few vague questions
- infer a route set informally
- start broad code changes
- backfill the docs later

That weakens the package exactly where design quality, delivery scope, and route ownership should first become durable.

## Target Outcome

After this phase, the package should make it explicit that broad implementation starts only after a compact pre-code artifact chain exists:

1. intake output or equivalent assumptions
2. design-system and route-doc baseline
3. implementation map tied to verification and route ownership

The package should make it natural to record:

- route inventory and route omissions
- current source-path choice and milestone target
- assumptions versus unresolved blockers
- design-doc readiness for core routes
- implementation order and verification destinations

## Scope

In scope:

- harden `zero-to-website-design/references/intake-brief.md`
- harden `zero-to-website-design/references/design-system-docs.md`
- harden `zero-to-website-design/references/implementation-map.md`
- align `zero-to-website-design/SKILL.md`
- align `docs/usage/zero-to-website-design.md`
- align `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- adding scripts or automation
- changing provenance statuses
- changing QA evidence schemas
- adding new templates
- changing unrelated packages or repository-level docs

## Concrete Gaps To Close

### 1. Intake output is still too easy to treat as optional

The intake brief defines useful prompts, but it does not strongly say that the inferred or collected brief must be preserved in project docs before concept expansion or implementation continues.

### 2. Design-doc readiness is underspecified

The design-system-doc reference lists required docs, but it does not yet explicitly require route inventory, source-path choice, milestone state, and route-spec coverage to be visible before broad editing starts.

### 3. Implementation mapping does not explicitly fail closed on missing docs

The implementation-map reference explains how to map routes, but it should be clearer that missing intake/design/source docs are blockers for broad implementation rather than nice-to-have follow-ups.

### 4. Public workflow wording underplays the pre-code gate

`SKILL.md` and the usage guide should make the pre-code artifact chain obvious so a future session understands the package's order of operations without needing to infer it from multiple references.

## Proposed Changes

### `references/intake-brief.md`

Add stronger wording for:

- preserving a compact intake output before implementation
- recording milestone target and source-path choice
- distinguishing assumptions from open blockers
- naming route types that are intentionally deferred

### `references/design-system-docs.md`

Add a stronger document gate covering:

- intake or assumption source
- route inventory and route omissions
- source-path summary and milestone target
- page-spec coverage for touched core routes
- implementation plan presence before broad edits

### `references/implementation-map.md`

Add explicit prerequisite and blocker wording for:

- intake output or equivalent brief
- visual source map
- core route docs
- milestone target and verification destination

Also tighten the output example so another session can see deferred routes, blockers, and evidence destination before code begins.

### `SKILL.md`

Clarify that:

- intake output must be recorded before concept expansion or broad implementation
- design docs and implementation map are a pre-code gate, not post-hoc paperwork
- broad implementation begins only after the artifact chain exists

### `docs/usage/zero-to-website-design.md`

Add a compact "Pre-Code Document Gate" section so users can understand the workflow order quickly from the public usage doc.

### Tests

Expand package tests so the repo proves the package now requires:

- preserved intake output
- explicit route omissions and milestone choice
- pre-code artifact gating across intake, design docs, implementation map, skill text, and usage docs

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- intake guidance clearly requires a preserved brief or equivalent assumptions before broad implementation
- design-doc guidance clearly defines the pre-code gate
- implementation-map guidance clearly treats missing prerequisite docs as blockers
- `SKILL.md` and usage docs reflect the stricter order of operations
- tests lock the new wording
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use a pre-code document-gate hardening pass as the next `zero-to-website-design` stage.
- Rationale: The later-stage provenance, QA, and delivery contract is already much stronger than the package's intake-to-implementation handoff. Tightening the earlier gate has higher leverage than adding yet another later-stage artifact.
- Risk: The workflow could feel heavier for tiny sites.
- Mitigation: Keep the required artifacts compact, allow equivalent project docs, and focus only on information that materially controls implementation.

## Suggested Commit Shape

- `feat(阶段20): harden pre-code document gate`
