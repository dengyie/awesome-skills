# Zero-To-Website Design V19 Entrypoint And Usage Visibility Plan

> Status: Draft for implementation
> Target package: `zero-to-website-design`
> Phase type: entrypoint documentation hardening

## Goal

Make the package entrypoint and public usage text expose the stronger delivery vocabulary earlier, so a user can see the expected route-mockup, temporary-binding, and delivery-handoff rules without first reading the deeper references.

## Why This Phase

The package already has strong internal contracts for:

- historical mock handling
- provenance and authority
- generated route mockups
- framework-first delivery
- delivery handoff continuity

But the top-level entry text still leads with a lighter brief-to-QA summary. That is correct, but it does not surface the strongest workflow commitments soon enough for a user deciding how to start.

## Target Outcome

After this phase, the package entrypoint should make it obvious that:

- historical repo images are first-class inputs
- `Framework Ready` and `Visual Delivery Ready` are distinct milestones
- generated route mockups must carry explicit route ownership and escalation detail
- temporary-binding assets must be acknowledged in delivery notes
- handoffs must preserve the weakest route, active escalation target, and next verification target

## Scope

In scope:

- harden `zero-to-website-design/SKILL.md`
- harden `docs/usage/zero-to-website-design.md`
- align `zero-to-website-design/agents/openai.yaml`
- expand `zero-to-website-design/tests/test_skill_package.py`

Out of scope:

- new references
- route acceptance wording changes
- production delivery wording changes
- memory workstream structure changes

## Concrete Gaps To Close

### 1. Entrypoint summary still under-signals the strongest delivery rules

The package entry text names the workflow, but it does not foreground the route-mockup and handoff obligations that now govern the later stages of a real pass.

### 2. Public usage examples are strong but still slightly too generic

The usage doc already lists workflows, yet the examples still read as generic prompts instead of showing the stricter framework-first and handoff-aware expectations first.

### 3. Platform metadata is too compact for the expanded package story

`openai.yaml` still summarizes the package as a simple brief-to-QA workflow. The package is broader now, and the metadata should carry that without becoming noisy.

## Proposed Changes

### `SKILL.md`

Add a short opening emphasis that:

- historical mockups are preferred when available
- generated route mockups need explicit ownership and coverage
- `Framework Ready` is an acceptable milestone when final art is still provisional
- final delivery must preserve weakest-route and escalation context

### `docs/usage/zero-to-website-design.md`

Add a brief entry section that:

- points users toward the historical mock and framework-first path
- calls out generated route mockups as route-specific, not just concept art
- clarifies that handoff notes should preserve the weakest route and next verification target

### `agents/openai.yaml`

Expand the default prompt so it mentions:

- design docs
- visual sources
- route specs
- browser QA
- delivery handoff

### Tests

Expand package tests so the repo proves:

- the skill entrypoint still names historical mock and framework-first delivery
- the usage doc now exposes the route-mockup and handoff expectations earlier
- the agent metadata prompt mirrors the stronger package scope

## Test Plan

- `python -m unittest discover E:\\project\\blog\\awesome-skills-worktrees\\zero-to-website-v11-clean\\zero-to-website-design\\tests -v`
- `python C:\\Users\\mango\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py E:\\project\\blog\\awesome-skills-worktrees\\zero-to-website-v11-clean\\zero-to-website-design`
- `python E:\\project\\blog\\awesome-skills-worktrees\\zero-to-website-v11-clean\\production-code-quality-review\\scripts\\review-entrypoint.py --repo E:\\project\\blog\\awesome-skills-worktrees\\zero-to-website-v11-clean --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- entrypoint text surfaces the stronger delivery vocabulary earlier
- usage docs show the framework-first and handoff-aware path more explicitly
- agent metadata matches the broader package scope
- tests lock the contract
- validation passes
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use entrypoint and public usage visibility hardening as the V19 stage for `zero-to-website-design`.
- Rationale: The internal workflow is already strict, but the user-facing entry text should surface the strongest delivery obligations earlier so the package is easier to start correctly.
- Risk: The entry text could become too dense.
- Mitigation: Keep the wording compact and reserve the deeper rule detail for the references.

## Suggested Commit Shape

- `feat(阶段28): harden entrypoint and usage visibility`
