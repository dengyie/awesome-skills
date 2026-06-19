# Zero-To-Website Design V22 User-Selected Visual Direction Gate Plan

## Problem

Recent real usage showed that `zero-to-website-design` can still let an agent treat a text-only visual direction or engineering scaffold as enough authority for a from-zero website. The workflow mentions concept directions and user selection, but the requirement is too conditional and easy to bypass before implementation.

## Goal

Make user-selected visual direction a hard pre-code gate for from-zero websites when no binding visual source exists and the target is more than a framework-only scaffold.

## Scope

- Strengthen `SKILL.md` so from-zero visual direction choice is a material decision that cannot be assumed.
- Strengthen `concept-generation.md` so 2-4 candidate visual images or homepage mockups must be shown and selected before visual implementation.
- Strengthen `visual-provenance.md` so unselected concepts cannot become binding route authority.
- Strengthen delivery docs so `Framework Ready` is clearly limited when no user-selected visual direction exists.
- Add regression coverage in `zero-to-website-design/tests/test_skill_package.py`.

## Out Of Scope

- Generating actual example images.
- Refactoring the whole website workflow.
- Changing unrelated skill packages.

## Acceptance

- Tests fail if the user-selected visual direction gate disappears.
- Skill validation passes.
- Local installed `zero-to-website-design` is synchronized after repository changes.
