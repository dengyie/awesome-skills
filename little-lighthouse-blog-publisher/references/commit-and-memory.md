# Commit And Memory

Use this reference after verification.

## Review

Use `production-code-quality-review` before committing.

For ordinary post packages:

```text
Review mode: checkpoint
Scope: content/posts/<slug>.*, public/posts/<slug>/, generated feed/sitemap output
Focus: correctness, publication leakage, route/feed inclusion, metadata quality, asset placement
```

Block commit for:

- build failure
- invalid required metadata
- missing body for a published post
- invalid category
- draft leaking into public output
- published post missing public route/feed/sitemap inclusion
- asset path mismatch

## Memory Updates

Update:

```text
.codex-memory/session-log.md
.codex-memory/decisions.md when a decision was made
.codex-memory/todo.md when follow-up remains
```

Session log entry:

```text
Task:
Actions:
Results:
Next:
Blockers:
```

For published posts, record slug, assets/fallbacks, verification commands, review outcome, and commit hash.

For drafts, record why it stayed draft and what is needed before publication.

## Commit Messages

```bash
git commit -m "feat(blog): publish <slug>"
git commit -m "chore(blog): add draft <slug>"
git commit -m "fix(blog): update <slug>"
```

Keep commits atomic: one post package or one coherent publishing change.

If the user asks not to commit, stop after verification and report uncommitted files.

## Final Report

Include:

```text
published or draft slug
files created or updated
assets used and fallbacks applied
validation commands and results
review status and score
commit hash when committed
remaining follow-up
```
