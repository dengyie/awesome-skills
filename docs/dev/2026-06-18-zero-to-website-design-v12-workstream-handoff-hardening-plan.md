# Zero-To-Website Design V12 Workstream And Handoff Hardening Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: continuity-contract hardening

## Goal

Tighten the package's long-running delivery continuity contract so another session can resume website work from filesystem artifacts without reconstructing route state, QA state, and delivery blockers from chat.

The package already enforces stronger provenance, QA evidence, delivery templates, and a pre-code document gate.

The remaining weak spot is continuity after implementation starts: the memory reference and workstream template still leave too much room for vague "resume later" notes that do not name the route matrix, evidence owner, next verification target, or handoff-critical blocker.

## Why This Phase

`zero-to-website-design` is explicitly meant to support long-running website delivery work.

Right now, the package already says:

- use `.codex-memory/` when present
- keep a website workstream up to date
- generate a handoff when another session must resume

But the current continuity surface still under-specifies:

- what must be preserved when a pass pauses midstream
- when route evidence gaps require a workstream update versus only a session note
- what a handoff must say about route owners, temporary assets, and next QA targets

That leaves the package vulnerable to a common failure mode: the website implementation may be good, but the next session still has to rediscover which routes were ready, blocked, provisional, or awaiting asset upgrades.

## Target Outcome

After this phase, the package should make it natural to preserve:

- the current route matrix slice
- weakest route evidence status
- temporary-binding assets still controlling routes
- exact next verification or implementation action
- blockers that another session must not infer from chat alone
- whether a dedicated handoff artifact is required now

## Scope

In scope:

- harden `zero-to-website-design/references/project-memory-integration.md`
- harden `zero-to-website-design/assets/templates/website-workstream.md`
- harden `zero-to-website-design/assets/templates/qa-report.md`
- align `zero-to-website-design/SKILL.md`
- align `docs/usage/zero-to-website-design.md`
- align `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- adding scripts or automation
- changing route evidence schema semantics
- adding new templates
- changing unrelated packages or repository-level docs

## Concrete Gaps To Close

### 1. Workstream updates do not yet require enough route-state continuity

The memory reference says when to update workstreams, but it does not strongly require that a workstream preserve the current route slice, weakest route status, or next evidence target.

### 2. Handoff generation criteria are still too soft

The current handoff section names common pause conditions, but it does not sharply state what makes a handoff mandatory versus merely helpful.

### 3. The shipped workstream and QA templates under-record resume-critical state

`website-workstream.md` and `qa-report.md` still leave too much room for vague next steps that do not name route readiness, evidence owner, follow-up route, or blocker ownership.

### 4. Public workflow wording underplays continuity as part of delivery quality

`SKILL.md` and the usage guide should make it obvious that long-running website work is not complete when the code exists but the continuation state only lives in chat.

## Proposed Changes

### `references/project-memory-integration.md`

Add stronger wording for:

- route-matrix continuity in workstreams
- weakest route evidence status tracking
- explicit handoff triggers tied to blocked routes, temporary assets, and unresolved QA follow-up
- minimum fields a handoff or resume note must preserve

### `assets/templates/website-workstream.md`

Add fields for:

- current route matrix slice
- weakest route evidence status
- next evidence target
- blocker owner
- handoff artifact status

### `assets/templates/qa-report.md`

Add fields for:

- route owner follow-up
- next-session verification target
- unresolved blocker owner
- handoff artifact link or status

### `SKILL.md`

Clarify that:

- long-running website work must preserve resume-critical route and QA state in project memory
- handoff generation is mandatory when another session would otherwise reconstruct delivery state from chat alone

### `docs/usage/zero-to-website-design.md`

Add a compact continuity section that explains how workstreams, QA reports, and handoffs should preserve the next session's starting point.

### Tests

Expand package tests so the repo proves the continuity contract now requires:

- explicit workstream route-state preservation
- handoff triggers tied to blocked or provisional delivery state
- resume-critical wording across references, templates, skill text, and usage docs

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- memory integration guidance clearly defines when continuity artifacts must be updated
- workstream and QA templates preserve resume-critical route and blocker state
- `SKILL.md` and usage docs reflect the stricter continuity contract
- tests lock the new wording
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use workstream-and-handoff continuity hardening as the V12 stage for `zero-to-website-design`.
- Rationale: After V11, the package is stronger before code starts than after a long-running pass pauses. Tightening continuity has higher leverage than opening another unrelated reference pass.
- Risk: The workstream template could become too heavy for very small sites.
- Mitigation: Keep the new fields focused on resume-critical state only and allow equivalent local artifacts when they preserve the same information.

## Suggested Commit Shape

- `feat(阶段21): harden workstream handoff continuity`
