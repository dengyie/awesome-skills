# Troubleshooting

## `collect-review-context.py` does not suggest the references I expected

Possible reasons:

- the changed files do not expose the stack signal you expected
- the current working tree is too narrow to trigger a risk flag
- the repo shape suggests a different review path than you assumed

What to do:

- inspect `detected_stack`
- inspect `risk_flags`
- inspect `changed_files`

These three fields explain most routing behavior.

## The brief shows `Base: HEAD`

This means the helper could not confidently infer a better branch comparison target and fell back to the current working-tree scope.

This is normal for:

- brand new repositories
- repos without `origin/main` or `origin/master`
- local-only changes where no meaningful branch comparison exists

## The repo is dirty and the brief seems broad

The skill intentionally includes staged, unstaged, and untracked files when building working-tree scope.

If the scope is too broad:

- clean unrelated files
- stage only the intended subset
- re-run `collect-review-context.py`

## Why does the skill care about changed-line ranges?

Because they help suppress false positives:

- introduced issues are easier to isolate
- pre-existing issues are less likely to be misreported
- the final review can stay closer to the actual diff

## The skill suggests fewer references than I expected

That is usually intentional. The skill now prefers a smaller, higher-value reference set to reduce loading cost and browsing overhead.

## `review-entrypoint.py` is useful, but I still want raw data

Use:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

`review-entrypoint.py` is for fast human-readable briefing.

## A TypeScript repo only shows `typescript` without `frontend`

That is expected when the repo looks more like backend TypeScript than browser UI code. The routing logic tries to distinguish frontend-specific signals from general TypeScript service code.

## Tests pass locally, but Codex still gives a weak review

The skill is strongest when Codex can access:

- the repo
- the actual diff or working tree
- nearby implementation context
- tests

If you only give a short snippet, the review will still work, but it will naturally be lower confidence.
