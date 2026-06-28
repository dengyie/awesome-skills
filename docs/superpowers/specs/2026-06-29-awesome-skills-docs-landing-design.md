# Awesome Skills Docs Landing Design

Date: 2026-06-29
Status: Proposed and user-approved for spec drafting
Target scope: repository landing docs and newcomer navigation

## Goal

Refactor the repository's GitHub-facing documentation so a first-time visitor can answer four questions within one minute:

1. what is this repository
2. which skill should I use first
3. how do I install a skill
4. where do I go for deeper docs

The repository should present a short landing page first, then hand users into a stable documentation navigation layer instead of forcing them to scan long package-level detail on the homepage.

## Problem Statement

The current docs contain strong material but the first-run path is not shaped around repository discovery.

Main issues:

- `README.md` behaves like a mixed landing page, package catalog, manual, and maintainer note
- the most important newcomer question, "which skill should I use," is answered late instead of early
- `docs/usage/quickstart.md` is effectively package-specific today instead of repository-level
- `docs/usage/skill-matrix.md` is useful, but it is not clearly established as the primary routing page
- the Chinese overview exists, but its information architecture is not explicitly mirrored to the English landing structure
- deep docs, release notes, and historical design materials sit too close to the newcomer path

The result is that the repository is informative but not sharply navigable.

## Primary Audience

Primary audience:

- first-time GitHub visitors evaluating the repository
- users who want to choose the right skill before reading detailed package docs

Secondary audience:

- returning users who need a stable, predictable path back to install, routing, and deeper docs

This redesign is intentionally not maintainer-first.

## Success Criteria

The redesign succeeds when:

- `README.md` is visibly shorter and acts as a landing page instead of a manual
- the first recommended action from the repository homepage is to use the skill matrix
- installation instructions are short, unified, and no longer repeated in conflicting forms
- `docs/usage` behaves like a navigation layer rather than a loose set of pages
- `docs/zh/README.zh-CN.md` mirrors the same newcomer path as the English landing
- package-specific and maintainer-specific detail remains available through links rather than homepage expansion

## Non-Goals

This work does not:

- rewrite every skill usage guide from scratch
- fully localize every English usage page into Chinese
- redesign package internals or technical canonical docs
- reorganize release-note history
- create a new contributor handbook in this milestone

## Design Principles

The landing system should follow these principles:

1. route before explain
2. homepage first, manual second
3. one stable installation story
4. mirrored top-level English and Chinese entry structure
5. preserve deep docs, but demote them out of the first-run path

## Information Architecture

The newcomer doc path should become:

`README.md` -> `docs/usage/skill-matrix.md` -> skill-specific guide or common support doc

Parallel support path:

`README.md` -> `docs/usage/quickstart.md`

Chinese mirrored path:

`docs/zh/README.zh-CN.md` -> Chinese support docs and English skill matrix / usage pages where needed

### Routing Roles

`README.md`

- GitHub landing page
- repository positioning
- skill selection entry
- install summary
- docs directory
- light maintainer pointer

`docs/usage/skill-matrix.md`

- primary routing page for choosing a skill
- expanded but still concise decision surface
- canonical answer to "which skill should I use first"

`docs/usage/quickstart.md`

- shortest successful repository-level install and verification path
- no deep package walkthroughs

`docs/usage/<skill>.md`

- skill-specific operating pages
- kept mostly intact, but aligned with shared top-of-page wording and navigation

`docs/zh/README.zh-CN.md`

- Chinese newcomer landing page
- same top-level structure as English
- explicit labeling when a deeper page is only available in English

## README Design

`README.md` should be reduced to seven sections.

### 1. Repository Positioning

A short opening that states:

- this repository is a collection of reusable Codex skills
- the collection is oriented toward evidence-first, production-minded delivery
- the repository ships multiple independent skill packages

### 2. Choose A Skill

A compact matrix or table should appear near the top.

Each skill entry should expose only the minimum routing fields:

- skill name
- when to use
- what problem it is best for
- documentation link

This section is the primary call to action.

### 3. Recommended Starting Points

This section should route common newcomer intentions:

- "I do not know which skill to use" -> `docs/usage/skill-matrix.md`
- "I want the fastest install path" -> `docs/usage/quickstart.md`
- "I prefer Chinese docs" -> `docs/zh/README.zh-CN.md`

### 4. Install

The install section should be short and repository-wide.

It should include:

- supported install roots
- one copy example
- a brief reload/restart note

It should not include:

- long package-specific helper script detail
- multiple alternative command blocks for every package
- maintainer troubleshooting detail

### 5. Docs

This section should link the stable top-level destinations:

- quickstart
- skill matrix
- FAQ
- troubleshooting
- review workflows
- Chinese overview
- release notes index

### 6. Repository Layout

This should stay high-level and explain only the main directory categories, not every file behavior.

### 7. For Maintainers

This should remain intentionally small and point maintainers toward:

- package tests
- release notes
- deeper development docs

The maintainer path must exist, but it must not dominate the homepage.

## Usage Layer Design

`docs/usage` should become a deliberate navigation layer.

### `quickstart.md`

This page should be rewritten as a repository quickstart, not a `production-code-quality-review` quickstart.

It should answer:

- where skills are installed
- how to install one skill
- how to reload skills
- how to verify discovery
- where to go next if the user needs help selecting a skill

It should explicitly avoid:

- long review-tool examples
- package-specific CLI walkthroughs
- detailed verification commands for one package only

### `skill-matrix.md`

This page should remain the core routing artifact, but be tightened around consistent decision fields.

Each skill should use a shared schema:

- `When to use`
- `Best for`
- `Avoid when`
- `Typical outputs`
- `Docs`

This page should also include:

- a short "pick by problem type" section
- a short "pick by expected output" section
- minimal prompt starters

It should not become a second homepage or a second manual.

### Skill-Specific Usage Pages

These pages should keep their existing substantive guidance, but their openings should be normalized.

Each page should begin with a short shared pattern:

- one-sentence purpose
- when to use it
- what it produces
- where to go if the user is still choosing among skills

Each page should also gain a short related-docs area if it does not already have one.

## Chinese Mirroring Strategy

The Chinese overview should mirror the English landing structure without requiring full one-to-one translation of every downstream page.

### Mirror Contract

`docs/zh/README.zh-CN.md` should mirror the same top-level sections as `README.md`:

1. repository positioning
2. choose a skill
3. recommended starting points
4. install
5. docs
6. repository layout
7. for maintainers

### Localization Rules

- keep skill IDs in English
- keep commands, paths, and filenames unchanged
- use concise Chinese wording adapted for readability, not literal translation
- explicitly mark when the next linked page is English-only

### Scope Boundary

This milestone only guarantees a mirrored Chinese landing experience, not fully mirrored deep usage coverage.

## Content Demotion Rules

The redesign should preserve deep material but move it off the first-run path.

Demote from the homepage:

- long package-by-package prose blocks
- package-specific script walkthroughs
- detailed release history callouts
- historical development plans and design artifacts
- maintainer-only operational detail

Keep discoverable through links:

- release note index
- usage guides
- package READMEs
- technical design docs
- development history

## File Scope

### Files To Rewrite

- `README.md`
- `docs/usage/quickstart.md`
- `docs/usage/skill-matrix.md`
- `docs/zh/README.zh-CN.md`

### Files To Lightly Sync

- `docs/usage/best-project-memory.md`
- `docs/usage/evidence-driven-bugfix.md`
- `docs/usage/little-lighthouse-blog-publisher.md`
- `docs/usage/split-image-assets.md`
- `docs/usage/zero-to-website-design.md`

Light sync means:

- unify page openings
- add or normalize related-docs links
- remove obvious newcomer-path drift where needed

### Files Explicitly Out Of Scope

- package `SKILL.md` files
- release-note contents
- `docs/superpowers/` canonical package designs unrelated to this landing work
- broad maintainer or contributor process expansion

## Verification Strategy

This is a documentation information-architecture change, so verification is content- and navigation-based.

Required checks:

1. confirm every top-level landing link resolves
2. confirm `README.md` is shorter and visibly landing-oriented
3. confirm `quickstart.md` is repository-level, not package-level
4. confirm the Chinese overview mirrors the English section structure
5. confirm skill usage pages point back into the shared newcomer navigation

## Risks And Mitigations

### Risk: README becomes too sparse

Mitigation:

- keep the skill matrix on the homepage
- keep install and docs links visible without scrolling through a long manual

### Risk: usage docs remain stylistically inconsistent

Mitigation:

- limit this milestone to intro-section normalization and navigation sync
- defer large content rewrites

### Risk: English and Chinese docs drift again

Mitigation:

- define a strict mirrored top-level section contract
- keep the mirrored scope intentionally shallow and stable

## Acceptance Criteria

The milestone is ready for implementation when the resulting docs can satisfy all of the following:

- a newcomer can identify the right starting document from `README.md` in under one minute
- `skill-matrix.md` is the explicit primary destination for skill selection
- `quickstart.md` teaches only the shortest install-and-discovery path
- the Chinese overview follows the same entry architecture as the English landing
- deep package and maintainer detail is still accessible, but no longer competes with the landing path

## Implementation Handoff

The next step after this approved spec is to write a milestone-scoped implementation plan for the landing-doc refresh.

That implementation plan should:

- stay within the rewritten landing and navigation layer
- prioritize repository-first newcomer flow over deep content expansion
- separate rewrite targets from light-sync targets
- define verification around link integrity and newcomer routing clarity
