# Asset Guidelines

Use this reference when collecting article images.

## Supported Assets

```text
thumbnail.png
hero.png
og.png
```

`thumbnail.png` is for card-safe small surfaces.

`hero.png` is for article detail hero surfaces.

`og.png` is for social previews, ideally 1200x630.

## Intake Modes

```text
none:
  no assets; use defaults
paths:
  user provides local paths
existing:
  assets already exist under public/posts/<slug>/
generate-requested:
  user explicitly asks AI to generate image assets
```

## Rules

- Assets are user-provided by default.
- Missing assets are allowed.
- Report every fallback in preview and final response.
- Normalize nonstandard filenames into supported names only after confirmation.
- Warn when an asset is clearly the wrong shape.
- Never overwrite existing assets without explicit confirmation.
- Do not generate images unless explicitly requested.

## Fallback Report

Use this shape:

```text
thumbnail: not provided; category default will be used
hero: not provided; site folk illustration fallback will be used
og: provided by user
```

If generated images are requested, confirm visual direction, target filenames, and whether generated files may be committed.
