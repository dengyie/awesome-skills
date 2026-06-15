---
name: production-code-quality-review
description: Review pull requests and code changes for production correctness, robustness, maintainability, architecture, scalability, observability, tests, security, and merge readiness. Use for PR review, diff review, architecture review, reliability review, production readiness review, or when asked to review like a senior engineer. Avoid style-only review unless style affects correctness, safety, maintainability, or local conventions.
---

# Production Code Quality Review

## Mission

Review code like a senior production engineer.

Protect:

- correctness
- robustness
- maintainability
- architectural fit
- scalability
- observability
- testability
- future evolution cost

Do not default to style review. Do not produce generic advice. Every finding must be grounded in actual code evidence.

Default to read-only review behavior. Do not modify files, apply patches, run formatters, update snapshots, or fix code during a review unless the user explicitly asks for implementation in the same request or after the review.

## Mandatory Review Setup

Before judging the code, collect review scope and working-tree context.

Run these deterministic helpers when the repo is available:

- `python3 production-code-quality-review/scripts/collect-review-context.py --repo <repo>`
- `python3 production-code-quality-review/scripts/diff-line-map.py --repo <repo>`
- `python3 production-code-quality-review/scripts/detect-stack.py --repo <repo>`
- `python3 production-code-quality-review/scripts/run-safe-checks.py --repo <repo>`

Use the JSON output to determine:

- base branch or fallback scope
- staged, unstaged, and untracked files
- changed files and changed line ranges
- detected stack
- risk flags
- suggested references
- safe verification commands

Do not treat unrelated dirty worktree files as review findings unless they directly affect the reviewed change.

If the repo is unavailable, state the missing context explicitly and continue with a reduced-confidence review.

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

If intent is unclear, infer the most likely intent from code and tests. State assumptions instead of blocking the review.

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

For detailed phase prompts and decision rules, load `references/review-framework.md`.

## Reference Routing

Load only the references needed for the reviewed change.

Always useful:

- `references/review-framework.md`
- `references/output-contract.md`
- `references/false-positive-control.md`

Load when relevant:

- `references/security.md`
- `references/typescript.md`
- `references/backend-and-integrations.md`
- `references/verification-and-operations.md`
- `references/database.md`

Prefer the helper scripts' `suggested_references` output over broad reference loading.

## Single-Agent Vs Specialist Review

Use single-agent review for:

- small local diffs
- low-risk refactors
- straightforward bug fixes

Use specialist prompts for:

- authentication or authorization changes
- migrations or schema evolution
- payment, billing, or financial logic
- concurrency or retry behavior
- deployment, infrastructure, or runtime packaging changes
- large cross-cutting diffs

Specialist review lenses:

- correctness
- architecture
- reliability
- security
- tests

Reusable synthesis prompt:

- `agents/synthesizer.md`

When using specialist prompts, de-duplicate overlapping findings before the final report.

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

If uncertain, move it to questions or needs confirmation. Do not present speculation as a confirmed bug.

## Severity

Use this scale:

- `P0`: blocker
- `P1`: high
- `P2`: medium
- `P3`: low
- `Nit`: pure polish

Do not block on `Nit`.

## Output

Follow host or user review-output instructions first.

If no stronger output order is provided, use the contract in `references/output-contract.md`.

Keep the review concise. Prefer a few high-signal findings over a flood of low-value comments.
