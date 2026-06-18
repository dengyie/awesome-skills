# Verification Checklist

Use this reference after writing or repairing a package.

## Required Commands

Run:

```bash
npm.cmd run build
node scripts/verify-blog-package.mjs <slug>
```

Use `npm.cmd` on Windows.

## Published Post Checks

After build, `verify-blog-package` must prove:

- `content/posts/<slug>.md` exists
- `content/posts/<slug>.meta.json` exists
- required metadata and body are present
- `out/posts/<slug>.html` exists
- `out/posts.html` includes the post
- `out/categories/<category>.html` includes the post
- `public/rss.xml` includes the post
- `public/sitemap.xml` includes the post route

## Draft Checks

For `published: false`:

- validate Markdown and metadata files
- confirm draft state
- skip public output checks
- report that no public route/feed/sitemap inclusion is expected

## Existing Fidelity Checks

Run these when the new package could affect route surfaces:

```bash
node scripts/verify-posts-archive-fidelity.mjs
node scripts/verify-post-detail-fidelity.mjs
node scripts/verify-category-page-fidelity.mjs
```

## Failure Handling

- Fix blocking package errors.
- Rerun the smallest relevant verifier.
- Rerun build after file changes.
- Do not commit if build fails.
- Treat fallback warnings as acceptable only when reported and intentional.
