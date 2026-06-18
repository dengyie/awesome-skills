# Interaction State Machine

Use this reference for the staged conversation model and resume behavior.

## Stage Output Contract

Each stage must produce:

```text
1. Collected material
2. AI assessment and suggestions
3. Next required user decision or confirmation
```

Keep questions narrow. Ask for the next missing material instead of presenting a long checklist.

## Internal Ledger

Maintain this conversation-state ledger internally:

```text
intent:
  action:
  language:
  publicationState:
body:
  source:
  title:
  status:
metadata:
  slug:
  category:
  excerpt:
  tags:
  relatedPosts:
assets:
  thumbnail:
  hero:
  og:
fallbacks:
  thumbnail:
  hero:
  og:
confirmation:
  bodySuggestions:
  metadata:
  assetFallbacks:
  finalWrite:
```

The ledger is not a file. Derive the final preview from it.

## Stages

### 1. Intent

Confirm whether the user wants to:

- publish a new post
- update an existing post
- create a draft package
- validate or repair a package

Also confirm language and draft/published state. If the body looks incomplete, recommend draft.

### 2. Body

Accept Markdown, plain text, an outline, pasted notes, or an existing draft path. Analyze the body before moving on.

Classify readiness:

```text
ready
needs-light-edit
draft-only
blocked
```

Suggest title, opening, section, conclusion, heading, and code-block improvements. Do not rewrite the full article without consent.

### 3. Metadata

Propose slug, title, date, category, excerpt, author, published, featured, tags, relatedPosts, seoTitle, seoDescription, and summaryQuote. Ask for confirmation.

For Chinese titles, provide 2-3 readable English slug candidates.

### 4. Assets

Ask whether images exist. Confirm whether the mode is:

```text
none
paths
existing
generate-requested
```

Report fallbacks for missing images.

### 5. Final Preview

Show:

```text
Action:
Slug:
Title:
Language:
Published:
Category:
Files:
Assets:
Fallbacks:
Public routes:
Validation:
Review:
Commit:
```

Ask a clear final question:

```text
Confirm that I should generate the files, run validation, review, and commit this post?
```

Do not treat an old or vague "ok" as final write confirmation.

### 6. Write, Verify, Review, Commit

After final confirmation, write only confirmed files, verify, review, update memory, and commit.

## Resume Behavior

On resume:

1. read project memory
2. inspect `git status --short`
3. check target package files
4. reconstruct the latest safe stage
5. show known material and missing confirmations

If files already exist but were not verified, verify package shape first. Do not rewrite immediately.

If unrelated files are dirty, ignore them unless they affect the package.
