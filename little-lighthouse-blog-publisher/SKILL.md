---
name: little-lighthouse-blog-publisher
description: Publish, draft, update, validate, or repair Little Lighthouse blog post packages through a staged AI workflow. Use when the user wants to add a new blog post, turn notes into a post, update an existing post package, attach article assets, validate a post package, or prepare a draft without publishing. The skill manages content collection, metadata planning, asset fallback decisions, local file writing after confirmation, build verification, production review, memory updates, and atomic commits for the Little Lighthouse Next.js static blog.
---

# Little Lighthouse Blog Publisher

## Core Rule

Treat publishing as a staged conversation, not a CMS form. Collect intent, body, metadata, and optional assets in order; provide useful suggestions at each stage; show the complete publishing preview; write files only after explicit final confirmation.

Do not publish directly from GitHub Pages, ask for GitHub tokens, create a browser upload flow, or invent assets unless the user explicitly asks for generated images.

## Required Startup

When invoked inside the Little Lighthouse repo:

1. Read `.codex-memory/project-state.md`, `.codex-memory/todo.md`, and the current `git status --short`.
2. Read `design-system/little-lighthouse-blog-publisher-skill-design.md` when implementation details are unclear.
3. Read `docs/superpowers/specs/2026-06-17-blog-publishing-package-design.md` before changing package structure.
4. Inspect `src/data/publishing/categories.ts`, `src/data/publishing/defaults.ts`, and `src/data/publishing/authors.ts` before proposing metadata.

If the current directory is not the Little Lighthouse repo, ask for the repo path before writing files.

## Workflow

Use this state machine:

```text
START
  -> INTENT_CONFIRMED
  -> BODY_COLLECTED
  -> META_CONFIRMED
  -> ASSETS_CONFIRMED
  -> PREVIEW_CONFIRMED
  -> FILES_WRITTEN
  -> VERIFIED
  -> REVIEWED
  -> COMMITTED
  -> DONE
```

For the stage rules, read `references/interaction-state-machine.md`.

## Package Contract

The blog package shape is:

```text
content/posts/<slug>.md
content/posts/<slug>.meta.json
public/posts/<slug>/thumbnail.png  optional
public/posts/<slug>/hero.png       optional
public/posts/<slug>/og.png         optional
```

Markdown owns body content. `.meta.json` owns publishing metadata. Missing images are allowed and must be reported as intentional fallback use.

For detailed field, category, draft, and route rules, read `references/package-contract.md`.

## Editorial And Metadata Suggestions

Before writing files, propose:

- title and slug
- publication state
- category
- excerpt and SEO description
- tags
- related posts
- whether the body is ready, needs light edits, should stay draft, or is blocked

For language-specific guidance and quality checks, read `references/editorial-guidelines.md`.

## Assets

Ask whether the user has images. Supported names are `thumbnail.png`, `hero.png`, and `og.png`.

Use user-provided paths only after confirmation. Do not overwrite existing assets without explicit confirmation. If assets are missing, continue with fallback behavior and report it in the preview and final response.

For asset intake and fallback details, read `references/asset-guidelines.md`.

## Verification

After writing files, run:

```bash
npm.cmd run build
node scripts/verify-blog-package.mjs <slug>
```

For published posts, also confirm detail route, posts archive, category archive, RSS, and sitemap inclusion. For drafts, validate the source package and skip public-output checks.

For the full command matrix and failure handling, read `references/verification-checklist.md`.

## Review, Memory, And Commit

Before committing, use `production-code-quality-review` in checkpoint mode for ordinary post packages. Fix blockers and rerun verification.

Update project memory and create an atomic commit unless the user explicitly asks not to commit.

For commit messages, memory entries, and final report shape, read `references/commit-and-memory.md`.

## Safety Gates

- Never write files before showing the final publishing preview and receiving explicit confirmation.
- Never delete a post or asset inside the normal publishing path.
- Never stage unrelated dirty worktree files.
- Never change publishing schema, route UI, or build behavior unless the user request and project docs explicitly require it.
- If a target file exists unexpectedly, stop and ask before overwriting.
