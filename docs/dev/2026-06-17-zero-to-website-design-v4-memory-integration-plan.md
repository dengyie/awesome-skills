# Zero-To-Website Design V4 Memory Integration Plan

> Status: In progress.
> Target package: `zero-to-website-design`
> Integration level: Level 3 governance-aware

## Goal

Integrate `zero-to-website-design` with `best-project-memory` as a real Level 3 consumer so the skill does not merely read context, but also participates in project memory governance during long-running website delivery work.

This phase should make the package explicitly capable of:

1. restoring repo memory before website work
2. using a dedicated workstream for route or delivery effort
3. recording durable design decisions
4. generating handoff expectations when the work pauses midstream
5. appending session evidence after meaningful progress

## Why This Phase

The current package already says "restore project context" and now has stronger delivery semantics after V3.

What it still lacks is an explicit memory governance contract:

- where website work should live inside `.codex-memory/`
- when route or delivery work becomes a workstream
- when temporary-binding choices become durable decisions
- when a handoff should be generated
- what should be appended to session history after a meaningful website work block

Without that contract, the workflow is strong but still too chat-dependent for interrupted multi-session delivery.

## Scope

In scope:

- update `zero-to-website-design/SKILL.md` so project memory is a required workflow participant, not just optional context
- add a new reference:
  - `references/project-memory-integration.md`
- update usage docs to explain how website work maps into `.codex-memory/`
- expand package tests so the new memory integration reference and workflow language are protected
- keep the integration documentation compatible with the existing `best-project-memory` helper scripts
- run tests, validation, and `production-code-quality-review`
- fix confirmed review findings

Out of scope:

- bundling direct shell wrappers that invoke `best-project-memory` scripts automatically
- changing `best-project-memory` data schemas in this phase
- implementing browser QA automation code in this skill package
- introducing website-project-specific file paths outside the documented examples

## Integration Design

### Memory objects this skill should read

Always read when present:

- `.codex-memory/project-state.md`
- `.codex-memory/todo.md`

Read when relevant:

- `.codex-memory/workstreams/<website-workstream>.md`
- latest relevant handoff under `.codex-memory/handoffs/`

### Memory objects this skill should update

After meaningful progress:

- append `session-log.md`
- refresh `todo.md`
- update `project-state.md` when milestone, blocker, or focus changes

For bounded website effort:

- create or update a workstream file such as:
  - `website-delivery.md`
  - `route-framework.md`
  - `visual-qa-pass.md`

For durable design decisions:

- promote to `decisions.md`

For paused multi-step work:

- generate or update a handoff document

### Website-specific trigger rules

Create or update a workstream when:

- route implementation spans multiple sessions
- QA or framework passes have their own blockers and next actions
- mock-asset integration becomes a separate delivery track

Promote a decision when:

- visual provenance authority becomes binding
- a framework-first milestone is accepted as the current delivery target
- an asset strategy becomes policy for the project
- a route structure or content strategy becomes durable

Generate a handoff when:

- the project pauses after design docs but before implementation
- framework-ready routes still require asset upgrades or QA
- browser QA uncovered issues that another session must continue

Append a session entry when:

- a route group was implemented
- design docs were materially updated
- QA was run
- production review was completed

## Package Changes

### Add

- `zero-to-website-design/references/project-memory-integration.md`
- `docs/dev/2026-06-17-zero-to-website-design-v4-memory-integration-plan.md`

### Modify

- `zero-to-website-design/SKILL.md`
- `docs/usage/zero-to-website-design.md`
- `zero-to-website-design/tests/test_skill_package.py`
- `CHANGELOG.md`

## Documentation Direction

The new reference should define:

- the expected `.codex-memory/` read order
- recommended website workstream naming
- when to use `promote_decision.py`
- when to use `generate_handoff.py` or `handoff_pack.py`
- how to summarize route, asset, QA, and delivery progress in session logs

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python -m unittest discover best-project-memory/tests -v`
- `python -m unittest discover production-code-quality-review/tests -v`
- `python %USERPROFILE%/.codex/skills/.system/skill-creator/scripts/quick_validate.py E:/project/blog/awesome-skills/zero-to-website-design`
- `python production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown`

## Acceptance Criteria

- `zero-to-website-design` explicitly references project memory governance in `SKILL.md`
- a dedicated `project-memory-integration.md` reference exists
- usage docs explain how website delivery maps to `.codex-memory/`
- tests prove the memory integration reference exists and is named by the skill
- tests prove memory workflow language covers workstreams, decisions, and handoffs
- validation passes
- `production-code-quality-review` review is run and confirmed findings are fixed

## Tasks

- [ ] Add the project-memory integration reference.
- [ ] Update `SKILL.md` and usage docs for Level 3 memory behavior.
- [ ] Expand tests for memory integration language.
- [ ] Run validation and tests.
- [ ] Run production review and fix findings.
- [ ] Update project memory with the new stage results.
- [ ] Commit and push.
