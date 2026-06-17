# Zero-To-Website Design V16 Asset Authority And Handoff Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: asset-contract hardening

## Goal

Tighten the package's asset-level authority and handoff contract so visual-source artifacts are strong enough to preserve which assets still control routes, what upgrade queue is active, what QA state each provisional asset still needs, and what another session must do next.

The package already has strong contracts for pre-code gating, route specs, content readiness, metadata integrity, browser QA, and delivery reporting. The remaining softer layer is the asset-level artifact set that sits between provenance and route execution.

## Why This Phase

`zero-to-website-design` already requires:

- provenance status and source method
- ownership scope such as route composition or texture-only
- milestone supported
- replacement trigger
- mock-asset notes for historical or temporary passes

But the current asset-facing artifacts still under-record several resume-critical facts:

- which route families are still controlled by the same provisional asset set
- whether an asset is actively blocking `Framework Ready` or only blocking `Visual Delivery Ready`
- which asset-specific QA or verification pass still needs to run
- whether the next session should upgrade the asset, validate it, or retire it
- which temporary-binding assets are part of the same upgrade queue

That leaves room for a long-running website project to preserve strong route docs while still having to reconstruct the active asset-upgrade state from chat or from scattered notes.

## Target Outcome

After this phase, the package should make it natural to preserve:

- asset-specific route family ownership
- readiness limiter for each provisional or generated asset
- asset-specific QA or verification state
- active upgrade queue membership
- blocker owner and next action for unresolved asset upgrades
- handoff notes strong enough for another session to resume the visual-source track directly

## Scope

In scope:

- harden `zero-to-website-design/references/visual-provenance.md`
- harden `zero-to-website-design/references/historical-mock-pass.md`
- harden `zero-to-website-design/references/project-memory-integration.md`
- harden `zero-to-website-design/assets/templates/visual-source-map.md`
- harden `zero-to-website-design/assets/templates/visual-source-inventory.md`
- harden `zero-to-website-design/assets/templates/mock-asset-pass.md`
- align `docs/usage/zero-to-website-design.md`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new automation scripts
- changes to route evidence status names
- changes to the existing route-data or metadata integrity contract
- new templates

## Concrete Gaps To Close

### 1. Asset artifacts still lag behind route-level continuity

The route spec and workstream can now hold strong blocker and handoff state, but the asset-facing docs still do not clearly say which provisional assets belong to the same active upgrade queue or which route families they still control together.

### 2. Asset readiness limiters are still too implicit

Current provenance rows record milestone and replacement trigger, but they do not clearly preserve whether a given asset blocks framework progress, visual delivery, or only final polish.

### 3. Asset QA and next-step ownership are too diffuse

The current templates mention QA at a high level, but they do not strongly capture the next verification target, blocker owner, or resume cue for the visual-source track itself.

## Proposed Changes

### `references/visual-provenance.md`

Clarify that binding and temporary-binding records should preserve:

- route family or route slice ownership
- readiness limiter
- active upgrade queue membership
- next verification target when the asset still needs QA or replacement

### `references/historical-mock-pass.md`

Clarify that mock-asset passes should preserve:

- grouped provisional asset tracks
- which routes or slots still depend on each track
- blocker owner and next upgrade action
- whether the next session is expected to validate or replace assets

### `references/project-memory-integration.md`

Extend the website-memory guidance so asset-source tracks are explicitly called out in workstreams or handoffs when they remain route-shaping.

### `assets/templates/visual-source-map.md`

Add columns or note fields for:

- route family
- readiness limiter
- upgrade queue
- next verification target
- blocker owner

### `assets/templates/visual-source-inventory.md`

Add lightweight fields for:

- route family
- readiness limiter
- next action
- blocker owner

### `assets/templates/mock-asset-pass.md`

Add fields for:

- active upgrade queue
- readiness limiter
- next verification target
- blocker owner
- whether the next session should validate, replace, or retire each provisional asset track

### `docs/usage/zero-to-website-design.md`

Add a short asset-authority continuity section that explains a visual-source artifact should be enough for another session to know:

- which provisional assets still shape routes
- which readiness ceiling they impose
- which asset queue is active
- who owns the next upgrade or verification action

### Tests

Expand package tests so the repo proves:

- visual provenance guidance now mentions route family, readiness limiter, upgrade queue, and next verification target
- visual-source and mock-asset templates carry the stronger asset-level continuity fields
- usage docs explain the new asset-authority continuity expectation
- memory guidance now names asset-source tracks as part of resumable website state

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\zero-to-website-design`
- `python E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills-worktrees\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- asset-facing provenance and mock-pass references preserve stronger upgrade and handoff state
- visual-source and mock-asset templates carry route-family, readiness-limiter, and next-step ownership fields
- usage docs expose the stronger asset-authority continuity expectation
- tests lock the new contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use asset authority and handoff hardening as the V16 stage for `zero-to-website-design`.
- Rationale: The package's route-level and delivery-level contracts are now strong, but the asset-level source artifacts still make another session reconstruct too much about provisional asset upgrades. Tightening that layer is the clearest next move.
- Risk: The templates could become too heavy for simple projects with only one or two local images.
- Mitigation: Keep the new fields focused on route-family ownership, readiness limiter, and next-step ownership instead of expanding into a full asset database.

## Suggested Commit Shape

- `feat(阶段25): harden asset authority handoff`
