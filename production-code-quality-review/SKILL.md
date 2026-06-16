---
name: production-code-quality-review
description: Use when reviewing pull requests, diffs, architecture-sensitive changes, reliability risks, production readiness, merge readiness, or requests to review like a senior engineer. Focuses on correctness, robustness, maintainability, observability, tests, security, and production risk rather than style-only review.
---

# Production Code Quality Review

## Mission

Review code like a senior production engineer.

Protect correctness, robustness, maintainability, architectural fit, scalability, observability, testability, and future evolution cost.

Do not default to style review. Do not produce generic advice. Every finding must be grounded in actual code evidence.

Default to read-only review behavior unless the user explicitly asks for implementation too.

## Mandatory Review Setup

Before judging the code, collect review scope and working-tree context.

Default entrypoint when the repo is available:

- `python3 production-code-quality-review/scripts/collect-review-context.py --repo <repo>`

Resolve `production-code-quality-review/scripts/...` relative to this skill directory. For a user-scope install, the absolute path is usually `$HOME/.agents/skills/production-code-quality-review/scripts/...`.

Use its output to determine scope, stack, risk flags, references, and verification commands.

Smaller helper scripts remain available for narrow automation or debugging:

- `diff-line-map.py`
- `detect-stack.py`
- `run-safe-checks.py`

Do not treat unrelated dirty worktree files as review findings unless they directly affect the reviewed change.

## Source Order

Inspect available context in this order:

1. User request and stated goal
2. Structured review context from the helper scripts
3. Git diff or changed files
4. Nearby surrounding code
5. Existing tests
6. README, architecture docs, ADRs, or design notes
7. Dependency files and generated artifacts when relevant
8. CI, deployment, logging, metrics, and operational paths when relevant

If intent is unclear, infer the most likely intent from code and tests. State assumptions instead of blocking.

## Review Workflow

Use this sequence for all non-trivial reviews:

1. Scope and intent
2. Correctness
3. Robustness
4. Architecture
5. Evolution and maintenance cost
6. Tests
7. Security, privacy, performance, and operational readiness when relevant
8. Verification pass for every candidate finding

Load `references/review-framework.md` for detailed phase prompts and decision rules.

## Reference Routing

Load only the references needed for the reviewed change.

Always useful:

- `references/review-framework.md`
- `references/output-contract.md`
- `references/false-positive-control.md`

Load when relevant:

- `references/security.md`
- `references/typescript.md`
- `references/python.md`
- `references/backend-and-integrations.md`
- `references/verification-and-operations.md`
- `references/database.md`

Prefer the helper scripts' `suggested_references` output over broad loading.

## Single-Agent Vs Specialist Review

Use single-agent review for small local diffs, low-risk refactors, and straightforward bug fixes.

Use specialist review lenses for auth, migrations, payments, concurrency, deployment, or large cross-cutting diffs:

- correctness
- architecture
- reliability
- security
- tests

Reusable synthesis prompt:

- `agents/synthesizer.md`

## Finding Rules

Every issue must include:

- Location
- Problem
- Impact
- Evidence
- Suggested fix
- Confidence
- New or pre-existing relative to the current change when that can be determined

Before reporting an issue, verify:

1. Is the issue reachable?
2. Is the triggering input or state realistic?
3. Is there existing code that already handles it?
4. Is it introduced or made worse by this change?
5. Is the impact significant enough to mention?

If uncertain, move it to questions. Do not present speculation as a confirmed bug.

## Severity

Use this scale:

- `P0`: blocker
- `P1`: high
- `P2`: medium
- `P3`: low
- `Nit`: pure polish

Do not block on `Nit`.

## Output

Follow host or user review-output instructions first. Otherwise use `references/output-contract.md`.

For automation, `review-entrypoint.py --format json` emits context shaped by `references/review-context.schema.json`. Individual findings should follow `references/finding.schema.json` when machine-readable output is needed.

Keep the review concise. Prefer a few high-signal findings over a flood of low-value comments.
