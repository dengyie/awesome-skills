# Zero-To-Website Design V3 Implementation Plan

> Status: In progress.
> Target package: `zero-to-website-design`
> Phase type: staged package evolution

## Goal

Implement the V3 historical-mock-first workflow so `zero-to-website-design` behaves like a stronger delivery playbook instead of a concept-generation-heavy orchestrator.

This phase should make four ideas explicit in the shipped package:

1. repo-owned or historical visual sources are first-class inputs
2. framework-first delivery is a valid milestone
3. temporary-binding visual authority is allowed but must be documented
4. production review remains required before final signoff

## Scope

In scope:

- update `zero-to-website-design/SKILL.md` workflow wording
- add the new references:
  - `references/historical-mock-pass.md`
  - `references/framework-first-delivery.md`
- add the new templates:
  - `assets/templates/mock-asset-pass.md`
  - `assets/templates/visual-source-inventory.md`
- revise the affected references so provenance, acceptance, and delivery match the V3 direction
- update usage documentation
- expand package tests to protect the new contract
- run validation, tests, and `production-code-quality-review`
- fix confirmed review findings
- record results in project memory and docs

Out of scope:

- adding browser automation scripts to the package
- creating install/update helper shells for this skill
- turning the package into a project-specific skill
- building a sample website implementation inside this repository

## Design Decisions

### Source-path priority

The V3 package should direct the agent to choose visual inputs in this order:

1. repo-owned final assets or user-approved references
2. approved historical mockups or prior project design images
3. local structural mock assets
4. newly generated images when still needed

### Provenance model

Replace the old broad statuses with:

- `exploratory`
- `candidate`
- `approved-direction`
- `binding-route`
- `temporary-binding`
- `obsolete`

Also add `existing-project-mockup` as a first-class source method.

### Delivery gates

Route acceptance must distinguish:

- `Framework Ready`
- `Visual Delivery Ready`

This should propagate into `route-acceptance.md`, `production-delivery.md`, usage docs, and tests.

## Files

Create:

- `zero-to-website-design/references/historical-mock-pass.md`
- `zero-to-website-design/references/framework-first-delivery.md`
- `zero-to-website-design/assets/templates/mock-asset-pass.md`
- `zero-to-website-design/assets/templates/visual-source-inventory.md`
- `docs/dev/2026-06-17-zero-to-website-design-v3-implementation-plan.md`

Modify:

- `zero-to-website-design/SKILL.md`
- `zero-to-website-design/references/concept-generation.md`
- `zero-to-website-design/references/visual-provenance.md`
- `zero-to-website-design/references/implementation-map.md`
- `zero-to-website-design/references/route-acceptance.md`
- `zero-to-website-design/references/production-delivery.md`
- `docs/usage/zero-to-website-design.md`
- `zero-to-website-design/tests/test_skill_package.py`
- `README.md` if package discovery text needs updating
- `CHANGELOG.md`

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python -m unittest discover production-code-quality-review/tests -v`
- `python %USERPROFILE%/.codex/skills/.system/skill-creator/scripts/quick_validate.py E:/project/blog/awesome-skills/zero-to-website-design`
- `python production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown`

## Acceptance Criteria

- `SKILL.md` explicitly supports historical mock and framework-first paths
- provenance documentation includes `temporary-binding`
- route acceptance distinguishes framework-ready from delivery-ready
- production delivery requires acknowledging temporary-binding assets
- tests prove the new references and templates exist
- tests prove the new provenance statuses and source methods are documented
- tests prove the workflow language no longer implies generation-first behavior
- validation passes
- `production-code-quality-review` review is run and confirmed findings are fixed

## Tasks

- [ ] Add V3 references and templates.
- [ ] Revise `SKILL.md` and affected references.
- [ ] Update usage docs and changelog text.
- [ ] Expand package regression tests.
- [ ] Run validation and tests.
- [ ] Run production review and fix findings.
- [ ] Update project memory and record stage results.
- [ ] Commit and push.
