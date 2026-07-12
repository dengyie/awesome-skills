# Systematic Skill Integration Fixes Design

## Objective

Fix the two confirmed repository defects without relying on one-off documentation edits:

1. every top-level skill package must be discoverable through the repository's public navigation and covered by package-level checks;
2. production review stack detection must not classify ordinary documentation containing the word `migration` as database code.

## Scope

The change covers `codex-agent-worktree-setup`, repository navigation tests, public English and Chinese entry documentation, and the stack-marker logic in `production-code-quality-review`.

The change does not redesign any skill workflow, add new Codex capabilities, or alter the meaning of genuine database migration paths.

## Package Integration Contract

`codex-agent-worktree-setup` will become a complete repository skill package by adding:

- `agents/openai.yaml` with the public display name, concise description, and trigger phrase;
- `tests/test_skill_package.py` covering required files, frontmatter/metadata alignment, and the worktree safety contract;
- `docs/usage/codex-agent-worktree-setup.md` with use cases, workflow, safety constraints, verification, and shared navigation links.

The top-level README, Skill Matrix, Chinese overview, repository layout, problem/output routing, and prompt starters will list the new package.

## Repository Discovery Contract

Repository-level tests will derive the authoritative skill set from top-level directories containing `SKILL.md`. A separately declared set of intentionally documented packages will be compared with that discovered set.

This keeps documentation expectations explicit while ensuring a newly added top-level skill cannot silently disappear from the public catalog. The regression test must fail before the documentation integration is added.

## Database Stack Detection Contract

Database detection will use explicit signals:

- `.sql` or `.sqlite` files;
- `schema.prisma`;
- paths whose directory segments include a recognized database migration directory such as `migration` or `migrations`.

A filename such as `docs/.../migration.md` is not a database signal. Existing real paths such as `migrations/001_init.sql` remain classified as database work.

The marker-selection and direct stack-detection paths will share the same predicate so their behavior cannot drift.

## Test Strategy

The implementation will follow two red-green loops:

1. add repository/package tests proving the seventh skill is absent from the current catalog and package contract; run them and confirm the expected failures; then add metadata and documentation until they pass;
2. add a review-library test proving `docs/.../migration.md` is not a database marker while real migration paths still are; run it and confirm failure; then introduce the narrow shared predicate.

After the targeted tests pass, run every package test suite, repository documentation tests, `git diff --check`, Python compilation without persistent bytecode artifacts, and a direct clean-repository context collection.

## Completion Criteria

- all seven top-level skill packages appear in English and Chinese public navigation;
- `codex-agent-worktree-setup` has metadata, usage documentation, and package tests;
- repository tests fail if a future top-level skill is omitted from the catalog contract;
- ordinary migration documentation does not select the database stack or `database.md`;
- genuine database migration files remain detected;
- the full repository test suite passes and both primary and feature worktrees remain clean apart from the intended committed changes.
