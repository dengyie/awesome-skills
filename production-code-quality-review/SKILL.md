---
name: production-code-quality-review
description: Evidence-first production code review SOP for pull requests, diffs, changed files, modules, architecture-sensitive changes, production-readiness checks, reliability reviews, maintainability reviews, robustness reviews, and merge-readiness decisions. Use when the user asks for code review, PR review, diff review, architecture review, reliability review, maintainability review, production readiness review, robustness review, "will this scale", "can this be merged", or "review this like a senior engineer". Avoid style-only review unless style affects correctness, maintainability, safety, or local conventions.
---

# Production Code Quality Review

## Mission

Review code like a senior production engineer. Protect correctness, robustness, maintainability, architectural fit, scalability, observability, testability, and future evolution cost.

Do not nitpick formatting. Do not produce generic advice. Every finding must be grounded in actual code evidence.

Default to read-only review behavior. Do not modify files, apply patches, run formatters, update snapshots, or fix code during a review unless the user explicitly asks for implementation in the same request or after the review.

## Source Order

Inspect available context in this order:

1. User request and stated goal
2. Git diff or changed files
3. Nearby surrounding code
4. Existing tests
5. README, architecture docs, ADRs, or design notes
6. Dependency files and generated artifacts when relevant
7. CI, deployment, logging, metrics, and operational paths when relevant

For git-based reviews, identify the review scope before judging the code: inspect status, determine the intended diff or base branch when available, distinguish staged, unstaged, and untracked files, and state assumptions when the target scope is inferred. Do not include unrelated dirty worktree changes as findings unless they affect the reviewed change.

If intent is unclear, infer the most likely intent from code and tests. State assumptions instead of blocking the review.

## Review Workflow

Use this sequence for all non-trivial reviews:

1. Scope and intent: identify what changed, affected modules, external systems, and risk level.
2. Correctness: review control flow, data flow, state transitions, input/output behavior, contracts, compatibility, and time/date logic.
3. Robustness: review errors, retries, timeouts, cancellation, idempotency, partial failures, cleanup, concurrency, and observability.
4. Architecture: review module boundaries, dependency direction, abstraction level, coupling, data ownership, and whether behavior lives in the right layer.
5. Evolution: review extensibility, migration path, feature toggles, schema/API evolution, reversibility, and six-month maintenance cost.
6. Tests: review whether tests would fail for the relevant bug, cover failure paths, and avoid shallow or over-mocked confidence.
7. Security/privacy and performance gates: run when touched surfaces make them relevant. Read `references/security.md` for authentication, authorization, user input, files, databases, secrets, tokens, payments, PII, network calls, admin features, serialization, template rendering, shell commands, dependencies, unsafe IO, rendering, hot paths, batch jobs, queues, caches, or operational-risk changes.
8. Verification pass: re-check every finding for reachability, evidence, severity, and false-positive risk.

For detailed phase prompts and checklists, read `references/review-framework.md` when the review is larger than a trivial local change.
For stack-specific risks, read only the relevant sections of `references/language-specific.md` for the languages and frameworks present in the reviewed code.

## Finding Rules

Every issue must include:

- Location: file, function, component, or behavior path
- Problem: what is wrong
- Impact: why it matters in production or maintenance
- Evidence: concrete code behavior, missing branch, reachable input, or changed contract
- Suggested fix: a direction that fits the existing codebase

Before reporting an issue, verify:

1. Is the issue reachable?
2. Is the triggering input or state realistic?
3. Is there existing code that already handles it?
4. Is it introduced or made worse by this change?
5. Is the impact significant enough to mention?

If uncertain, put it under questions or needs confirmation. Do not present speculation as a confirmed bug.

## Severity

Use this scale:

- `P0`: blocker. Data loss, critical exploitable security vulnerability, outage risk, broken core flow, irreversible migration risk, severe compatibility break, or incorrect financial/payment/security behavior.
- `P1`: high. Real correctness bug, serious edge-case failure, missing critical test, significant reliability problem, serious observability gap, or risky architectural coupling.
- `P2`: medium. Maintainability issue, moderate test gap, localized design problem, non-critical error handling weakness, or plausible future extension risk.
- `P3`: low. Readability, simplification, consistency, or documentation improvement.
- `Nit`: pure polish. Never block merge.

## Specialist References

Load references only when useful:

- `references/review-framework.md`: detailed review phases, verification pass, and final output structure.
- `references/security.md`: authentication, authorization, privacy, dependency, injection, unsafe IO, and performance/scalability gates.
- `references/language-specific.md`: TypeScript, Python, Go, Java, Rust, frontend, database, and API-specific review heuristics.

## Output

Follow host or user review-output instructions first. If no stronger output order is provided, use:

1. Top findings ordered by severity, with file/line references when available
2. Questions or needs confirmation
3. Architecture assessment
4. Robustness assessment
5. Test assessment
6. Meaningful strengths observed
7. Final recommendation: safe to merge, safe with follow-ups, fix before merge, or do not merge yet

Keep the review concise. Prefer a few high-signal findings over a flood of low-value comments.
