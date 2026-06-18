# Zero-To-Website Design V1 Hardening Plan

> Status: In progress.

## Goal

Harden `zero-to-website-design` from a valid v1 draft skill into a maintainable repository asset with first-use documentation and regression checks.

This phase should not change the skill's core behavior. It should make the existing package easier to discover, safer to edit, and easier to verify before future releases.

## Scope

In scope:

- Add repository-level usage documentation for `zero-to-website-design`.
- Add regression tests that protect the skill package shape and reference/template routing.
- Update repository README and changelog so the new docs and tests are visible.
- Run skill validation, test suites, and `production-code-quality-review`.
- Fix confirmed review findings.
- Commit and push the completed phase.

Out of scope:

- Add install/update shell scripts for `zero-to-website-design`.
- Add generated images or frontend code examples.
- Create Chinese mirror docs before the English workflow stabilizes.
- Change `zero-to-website-design` into a project-specific visual fidelity skill.

## Architecture

Keep `zero-to-website-design/SKILL.md` concise. Detailed onboarding belongs in `docs/usage/zero-to-website-design.md`; reusable agent instructions remain in `references/`; copyable project scaffolds remain in `assets/templates/`.

Add tests under `zero-to-website-design/tests/` so the skill package owns its own regression checks, mirroring the protected package pattern used by `production-code-quality-review`.

## Files

Create:

- `docs/usage/zero-to-website-design.md`
- `zero-to-website-design/tests/test_skill_package.py`

Modify:

- `README.md`
- `CHANGELOG.md`
- this development plan

## Test Plan

- `python -m unittest discover zero-to-website-design/tests -v`
- `python -m unittest discover production-code-quality-review/tests -v`
- `python %USERPROFILE%/.codex/skills/.system/skill-creator/scripts/quick_validate.py E:/project/blog/awesome-skills/zero-to-website-design`
- `python production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown`

## Acceptance Criteria

- A first-time user can find how to use `zero-to-website-design` from the root README.
- The usage doc explains both blank-brief and reference-image workflows.
- Tests prove all references and templates named by `SKILL.md` exist.
- Tests prove provenance statuses and source methods remain documented.
- Tests prove `agents/openai.yaml` has the required UI fields.
- Existing `production-code-quality-review` tests still pass.
- `zero-to-website-design` skill validation passes.
- `production-code-quality-review` review is run and confirmed findings are fixed.

## Tasks

- [x] Add usage documentation.
- [x] Add package regression tests.
- [x] Update README and changelog.
- [ ] Run validation and tests.
- [ ] Run production review and fix findings.
- [ ] Record results in this plan.
- [ ] Commit and push.
