# Awesome Skills V16 Four-Skill Doc Sync Plan

> Status: In progress.
> Target surface: repository-level public documentation
> Phase type: post-merge documentation alignment

## Goal

After merging `little-lighthouse-blog-publisher` into `main`, align the repository-facing docs so the project presents itself as a four-skill catalog instead of a three-skill catalog with one partially linked new package.

## Why This Phase

The merge added the new skill package and some README/matrix links, but several public navigation surfaces still describe the repository as if only three non-release-note packages existed.

The main risk is reader confusion:

- release indexes route only `best-project-memory` and `zero-to-website-design` as non-versioned package docs
- Chinese overview still says the repo contains three delivered skills
- the local verification block omits the new package test suite
- repository docs tests lock the older release-scope wording

## Scope

In scope:

- update English README release-scope and verification wording
- update English release index related docs and scope wording
- update Chinese overview and Chinese release index for the new skill
- keep `docs/usage/skill-matrix.md` consistent with four skills
- strengthen repository docs regression coverage
- record the doc-sync phase in project memory

Out of scope:

- changing runtime skill behavior
- adding formal versioned release notes for `little-lighthouse-blog-publisher`
- changing historical development notes except where a new V16 plan is needed

## Acceptance Criteria

- public docs clearly say the repo ships four skills
- release indexes explain that formal versioned release notes currently cover `production-code-quality-review`
- non-versioned package routing includes `best-project-memory`, `little-lighthouse-blog-publisher`, and `zero-to-website-design`
- local verification docs include the new skill test suite
- repository docs tests pass

## Test Plan

- `python -m unittest discover tests -v`
- `python -m unittest discover little-lighthouse-blog-publisher\tests -v`
- `git diff --check`
