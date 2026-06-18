# Package Contract

Use this reference before creating or updating package files.

## Files

Each post package uses:

```text
content/posts/<slug>.md
content/posts/<slug>.meta.json
public/posts/<slug>/thumbnail.png  optional
public/posts/<slug>/hero.png       optional
public/posts/<slug>/og.png         optional
```

## Ownership

- Markdown owns article body only.
- `.meta.json` owns publishing metadata.
- Frontmatter must not become the source of truth.
- If frontmatter conflicts with `.meta.json`, resolve or remove the conflict before publication.

## Required Metadata

```text
slug
title
date
category
excerpt
published
```

Recommended optional fields:

```text
readingTime
author
featured
tags
relatedPosts
seoTitle
seoDescription
summaryQuote
```

## Slug Rules

- lowercase kebab case
- short and stable
- unique for new posts
- English slugs for Chinese titles
- no silent suffixing when a slug exists; propose better options

## Category Rules

Read `src/data/publishing/categories.ts`.

Known mappings:

- `Java` -> `java`
- `Android` -> `android`
- `C++`, `cpp` -> `c-plus-plus`
- `Design Notes`, `design`, `static-web`, `static web` -> `design-notes`

Unknown categories require a recommendation and user confirmation.

## Draft And Published Behavior

`published: true` means the post should appear in public output:

- `/posts/<slug>`
- `/posts`
- `/categories/<category>`
- RSS
- sitemap

`published: false` means local draft only:

- validate source package
- skip public route/feed/sitemap expectations
- report that no public inclusion is expected

## Related Posts

- prefer same-category posts
- exclude self
- use 2-3 posts when useful
- never invent nonexistent slugs
- leave empty when there is no strong match
