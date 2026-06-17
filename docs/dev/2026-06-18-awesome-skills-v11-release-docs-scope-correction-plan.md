# Awesome Skills V11 Release-Facing Docs Scope Correction Plan

> Status: Draft for implementation
> Target surface: repository-level documentation
> Phase type: public docs alignment

## Goal

Correct the release-facing documentation surface so the repository no longer implies that release notes and public package history belong only to `production-code-quality-review`.

The repository front door already presents `awesome-skills` as a three-skill collection. But the release indexes still describe themselves as if they were only the release notes home for `production-code-quality-review`.

## Why This Phase

This is now the clearest remaining public-doc drift:

- `README.md` presents a multi-skill repository
- `docs/zh/README.zh-CN.md` presents a multi-skill repository
- `docs/releases/README.md` still presents a single-skill release directory
- `docs/zh/releases/README.zh-CN.md` still presents a single-skill release directory

That mismatch makes the repository feel narrower than it actually is and leaves no clear public place to explain which surfaces do or do not currently ship formal release notes.

## Target Outcome

After this phase:

- release-facing indexes describe the repository-level release surface accurately
- they explain that formal versioned release notes currently exist for `production-code-quality-review`
- they clearly route readers looking for the other shipped skills to usage docs and package entrypoints
- English and Chinese release indexes stay aligned

## Scope

In scope:

- harden `docs/releases/README.md`
- harden `docs/zh/releases/README.zh-CN.md`
- align `README.md` and `docs/zh/README.zh-CN.md` if needed so release links match the corrected framing
- expand repository-level regression coverage if needed
- update project memory for the new stage

Out of scope:

- creating formal versioned release-note files for `best-project-memory` or `zero-to-website-design`
- changing skill behavior
- changing package tests outside what is needed to protect the new docs contract

## Concrete Gaps To Close

### 1. Release indexes use the wrong ownership scope

They still say the directory contains the release notes for `production-code-quality-review`, instead of explaining the repository-level documentation surface.

### 2. Readers cannot tell which skills currently have formal release notes

The repository needs a short, explicit statement that versioned release notes are currently tracked for `production-code-quality-review`, while the other two skills are documented through usage guides and staged development notes.

### 3. English and Chinese release indexes should mirror the same scope contract

The Chinese mirror should say the same thing as the English release index, not preserve an older narrower framing.

## Proposed Changes

### `docs/releases/README.md`

Update it to:

- describe the release docs as a repository-level surface
- state which packages currently ship formal versioned release notes
- route readers to `docs/usage/` and skill entrypoints for the other packages

### `docs/zh/releases/README.zh-CN.md`

Mirror the same scope and routing in Chinese.

### `README.md` and `docs/zh/README.zh-CN.md`

Tighten release-links wording if needed so the release section clearly reads as repository-level navigation rather than as a hidden single-package sub-site.

### Tests

Add or extend regression coverage so the repository protects:

- repository-level release-surface wording
- explicit mention that current formal release notes are for `production-code-quality-review`
- cross-links to the other shipped skills' usage docs

## Test Plan

- `python -m unittest discover E:\project\blog\awesome-skills\zero-to-website-design\tests -v`
- `python C:\Users\mango\.codex\skills\.system\skill-creator\scripts\quick_validate.py E:\project\blog\awesome-skills\zero-to-website-design`
- `python E:\project\blog\awesome-skills\production-code-quality-review\scripts\review-entrypoint.py --repo E:\project\blog\awesome-skills --base HEAD --scope working_tree --format markdown`

## Acceptance Criteria

- English and Chinese release indexes describe the repository-level release surface accurately
- they clearly state which package currently has formal versioned release notes
- they route readers of the other two shipped skills to the correct docs
- tests protect the new wording if repository-level coverage is touched
- production review passes with no confirmed blocking issue

## Decision Record

- Decision: Use a release-facing docs scope correction as V11 instead of opening another `zero-to-website-design` contract hardening pass immediately.
- Rationale: The strongest remaining user-facing drift is no longer inside the skill package itself; it is in the repository-level release navigation that still implies a narrower package scope than the repo actually ships.
- Risk: Public docs changes can become vague if they try to describe too many package states at once.
- Mitigation: Keep the wording explicit about what formally ships today and route everything else to concrete usage docs.

## Suggested Commit Shape

- `docs(阶段19): correct release docs scope`
