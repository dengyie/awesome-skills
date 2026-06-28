# Little Lighthouse Blog Publisher

`little-lighthouse-blog-publisher` is a Codex skill for publishing posts into the Little Lighthouse blog repository through a staged AI workflow.

It belongs in this `awesome-skills` repository because it is reusable workflow logic. The actual blog resources, content packages, site code, images, and verifiers stay in `dengyie/dengyie.github.io`.

Use it when the main job is producing or updating a Little Lighthouse post package instead of building a generic publishing system.

## Best Fit

Use this skill when you want to:

- publish a new Little Lighthouse post from Markdown or notes
- create a draft-only post package
- update an existing post package
- attach or replace article assets
- validate that a post reaches detail, archive, category, RSS, and sitemap output
- keep the public GitHub Pages site static while Codex performs local publication work

Do not use it for:

- generic blog platforms
- building a browser CMS
- asking for GitHub tokens on the public site
- writing directly from GitHub Pages
- redesigning the Little Lighthouse UI

## What it produces

Typical outputs:

- a staged publication plan
- Markdown and `.meta.json` package updates
- asset fallback decisions
- verification results for the target blog repo

If you are still choosing among skills, go back to the [Skill Matrix](skill-matrix.md). If you only need installation help, use the [Quickstart](quickstart.md).

## Related docs

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [Examples](examples.md)
- [FAQ](faq.md)

## Source Split

Skill source:

```text
dengyie/awesome-skills/little-lighthouse-blog-publisher
```

Blog source:

```text
dengyie/dengyie.github.io
```

The blog repository owns:

- `content/posts/<slug>.md`
- `content/posts/<slug>.meta.json`
- `public/posts/<slug>/` assets
- `scripts/verify-blog-package.mjs`
- `/submit` static guide page
- RSS, sitemap, and route output

The skill owns:

- staged user interaction
- editorial and metadata suggestions
- asset fallback planning
- final confirmation before file writes
- verification and review sequence
- memory updates and commit guidance

## Workflow

The skill moves through this state machine:

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

The important boundary is `PREVIEW_CONFIRMED`: the skill must not write files until the user has seen the complete plan and explicitly confirmed it.

## Package Shape

Each post package uses:

```text
content/posts/<slug>.md
content/posts/<slug>.meta.json
public/posts/<slug>/thumbnail.png  optional
public/posts/<slug>/hero.png       optional
public/posts/<slug>/og.png         optional
```

Missing images are allowed. The skill should report which fallback will be used.

## Verification

After writing or updating a published post, the skill should run in the blog repository:

```bash
npm.cmd run build
node scripts/verify-blog-package.mjs <slug>
```

For route-sensitive changes, also run:

```bash
node scripts/verify-posts-archive-fidelity.mjs
node scripts/verify-post-detail-fidelity.mjs
node scripts/verify-category-page-fidelity.mjs
```

Draft posts with `published: false` validate the source package but skip public output checks.

## Prompt

```text
Use $little-lighthouse-blog-publisher to publish this Little Lighthouse Markdown draft as a blog post.
```

The skill will collect the article body, metadata, and optional images in stages before writing files.
