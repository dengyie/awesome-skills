# Review Workflows

This guide shows the main ways to use `production-code-quality-review`.

## Local Working Tree Review

Use this when you have uncommitted changes and want a production-style review before committing.

Suggested flow:

1. Collect context:

```bash
# Windows
python production-code-quality-review/scripts/collect-review-context.py --repo .

# POSIX
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

2. Generate the markdown brief:

```bash
# Windows
python production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown

# POSIX
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

3. Ask Codex to review the working tree with the skill:

```text
Use $production-code-quality-review to review my current working tree like a senior production engineer.
```

## Diff-Oriented Review

Use this when you care about what changed relative to the current branch base, not just the raw working tree.

The scripts automatically infer a base branch or fall back to `HEAD` when needed. The skill then uses:

- changed files
- changed-line ranges
- risk flags

to suppress unrelated findings.

If you need to force a review baseline or mode, `review-entrypoint.py` and `collect-review-context.py` both support:

- `--base <ref>`
- `--scope branch`
- `--scope working_tree`

## High-Risk Change Review

Use this when the change touches:

- auth or permissions
- payments or billing
- migrations
- retry, timeout, or concurrency behavior
- deployment or runtime packaging

In this mode, the skill may route toward a specialist review posture conceptually:

- correctness
- architecture
- reliability
- security
- tests

and then use the synthesis prompt to merge findings.

## Milestone Phase-Gate Review

Use this at the end of a bounded development phase when the current milestone has a frozen P0/P1 scope.

Suggested prompt:

```text
Use $production-code-quality-review as a phase-gate review for this milestone phase. Report 严重问题, 中等问题, 非阻塞建议, 安全风险, 稳定性风险, 可维护性风险, 测试覆盖, 质量评分, and 通过状态.
```

In this mode, the review should:

- block only on P0/P1 issues that prevent the current milestone's acceptance criteria
- send non-blocking suggestions to backlog
- record external dependencies as Manual-required
- avoid opening new phases for polish, unrelated cleanup, or long-term improvements

## Fast Human Briefing

Use this when you do not need a full Codex review yet and only want a compact summary of review scope and likely attention areas.

Run:

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

This is useful before:

- handoff
- code review
- PR creation
- release checks

## Machine-Readable Automation

Use this when you want the repo context in JSON for another tool, script, or workflow.

Run:

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

This is the best entrypoint for automation because it keeps the review scope deterministic.
