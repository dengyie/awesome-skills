# Awesome Skills Overview Doc Refresh Plan

## Background

The repository already contains multiple skill packages, but the top-level introduction is still weighted toward individual package notes and historical release details. A reader landing on the repository homepage should immediately understand what this repository contains, what each shipped skill does, and where to go next.

## Goal

Refresh the repository introduction docs so the overview page clearly answers:

1. what this repository is
2. which skills are included
3. what each skill is for
4. where each skill starts
5. which follow-up docs to read

## Scope

In scope:

- update `README.md` as the primary overview document
- update `docs/zh/README.zh-CN.md` so the Chinese introduction matches the current repository scope
- keep installation and documentation-entry guidance aligned with the current three-skill repository layout

Out of scope:

- adding new skills
- changing release notes
- changing package behavior or tests
- broad rewrites of usage guides unrelated to repository overview

## Content Changes

### README.md

- add a concise repository-level summary near the top
- add a clear "Included Skills" section that lists all shipped skills:
  - `best-project-memory`
  - `production-code-quality-review`
  - `zero-to-website-design`
- describe each skill in practical terms with:
  - problem it solves
  - best-fit use cases
  - entrypoint path
- simplify the information architecture so overview content appears before low-level command references
- keep the existing install and tooling guidance, but make it obvious that the repo is multi-skill rather than review-skill-only

### docs/zh/README.zh-CN.md

- rewrite the Chinese introduction around the full repository, not only `production-code-quality-review`
- add a Chinese version of the shipped skill inventory
- link to the key Chinese and English follow-up docs

## Verification

1. review the changed docs for consistency with the current repo layout
2. run `production-code-quality-review` against the working tree
3. stage, commit, and push the documentation update

## Expected Result

The repository homepage becomes a trustworthy catalog page for all shipped skills, and both English and Chinese introduction docs make the repository scope obvious within the first screenful.
