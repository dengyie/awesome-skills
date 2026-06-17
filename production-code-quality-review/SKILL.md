---
name: production-code-quality-review
description: Use when reviewing pull requests, diffs, architecture-sensitive changes, reliability risks, production readiness, merge readiness, or requests to review like a senior engineer. Focuses on correctness, robustness, maintainability, observability, tests, security, and production risk rather than style-only review.
---

# Production Code Quality Review

## Mission

Review code like a senior production engineer.

During active development, optimize for fast detection of core code risks.

Protect correctness first. Expand to broader production quality in deep and final reviews.

Do not default to style review. Do not produce generic advice. Every finding must be grounded in actual code evidence.

Default to read-only review behavior unless the user explicitly asks for implementation too.

## Review Modes

Default to `checkpoint` review during iterative development.

Use `deep` review when the core feature is implemented and the change needs a serious mid-stream review before final hardening.

Switch to `final` review only when the user explicitly asks for a full, comprehensive, final, pre-merge, release-readiness, or production-readiness review.

### Checkpoint Review

Use this for normal development checkpoints.

Primary goal:

- catch only the most important issues in the current change

Report only issues that are likely to cause one of these:

- wrong behavior
- crashes or hard failures
- data loss or data corruption
- broken public or cross-module contracts
- security or permission failures
- irreversible operational mistakes

In `checkpoint` mode:

- prioritize `P0`, `P1`, and only strong `P2`
- usually report at most `0-3` findings
- skip technical debt unless the current change is actively creating structural damage that will be expensive to unwind soon
- skip naming, style, polish, optional refactors, and broad architecture commentary
- skip pre-existing issues unless the current change clearly worsens them
- skip general observability and test wishlist comments unless the missing check directly hides a realistic bug in this diff
- do not open specialist review lenses unless risk flags show a clearly sensitive area like auth, payments, migrations, concurrency, or deployment

If no core issue is found, say so plainly instead of inventing follow-up work.

### Deep Review

Use this after the main functionality is complete but before final merge readiness.

This mode is for:

- large features that are functionally done
- core behavior that now needs a broad sanity pass
- major integration points that should be validated before polish and release hardening

In `deep` mode:

- review correctness, robustness, architecture, tests, security, and operational risk
- include meaningful technical debt if it is newly introduced or clearly expensive to unwind
- skip style-only feedback and shallow polish
- report `P0`, `P1`, and important `P2`
- keep the review focused on real issues, not speculative future work

### Final Review

Use this once the implementation is substantively complete.

In `final` mode, expand to the full production review:

- correctness
- robustness
- architecture
- evolution and maintenance cost
- tests
- security, performance, and operational readiness when relevant

This is the right place to surface broader maintainability concerns, non-trivial technical debt, incomplete coverage, and production hardening gaps.

## Mandatory Review Setup

Before judging the code, collect review scope and working-tree context.

Default entrypoint when the repo is available:

- `python3 production-code-quality-review/scripts/collect-review-context.py --repo <repo>`

Resolve `production-code-quality-review/scripts/...` relative to this skill directory. For a user-scope install, the absolute path is usually `$HOME/.agents/skills/production-code-quality-review/scripts/...`.

Use its output to determine scope, stack, risk flags, references, and verification commands.

Do not let setup become the expensive part of a checkpoint review. Collect enough context to inspect the changed behavior safely, then stop.

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

First decide the mode:

1. `checkpoint` for in-progress development
2. `deep` for completed core functionality that still needs a serious mid-stream review
3. `final` for explicit comprehensive review

Use this sequence for `checkpoint` reviews:

1. Scope and intent
2. Correctness of changed behavior
3. Failure handling only on the touched path
4. One verification pass for each candidate finding

Use this sequence for `final` reviews:

1. Scope and intent
2. Correctness
3. Robustness
4. Architecture
5. Evolution and maintenance cost
6. Tests
7. Security, privacy, performance, and operational readiness when relevant
8. Verification pass for every candidate finding

Use this sequence for `deep` reviews:

1. Scope and intent
2. Correctness
3. Robustness
4. Architecture
5. Evolution and maintenance cost
6. Tests
7. Security, privacy, performance, and operational readiness when relevant
8. Verification pass for every candidate finding

Load `references/review-framework.md` for detailed phase prompts and decision rules when running `deep` or `final` review, or when a checkpoint review touches a clearly high-risk surface.

## Reference Routing

Load only the references needed for the reviewed change.

Always useful:

- `references/output-contract.md`
- `references/false-positive-control.md`

Load by default for `deep` and `final` reviews and only when needed for higher-risk checkpoint reviews:

- `references/review-framework.md`

Load when relevant:

- `references/security.md`
- `references/typescript.md`
- `references/python.md`
- `references/backend-and-integrations.md`
- `references/verification-and-operations.md`
- `references/database.md`

Prefer the helper scripts' `suggested_references` output over broad loading.

## Single-Agent Vs Specialist Review

Use single-agent review for almost all checkpoint reviews, small local diffs, low-risk refactors, and straightforward bug fixes.

Use specialist review lenses mainly for deep and final reviews, or for checkpoint reviews that touch auth, migrations, payments, concurrency, deployment, or large cross-cutting diffs:

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

Checkpoint review bias:

- prefer silence over weak findings
- prefer one concrete blocker over five medium-confidence suggestions
- do not convert "could be nicer" into review debt
- do not ask for cleanup that is not necessary to keep current development safe

## Severity

Use this scale:

- `P0`: blocker
- `P1`: high
- `P2`: medium
- `P3`: low
- `Nit`: pure polish

Do not block on `Nit`.

In `checkpoint` mode:

- do not report `P3`
- do not report `Nit`
- report `P2` only when the issue is concrete, reachable, and worth fixing now
- default recommendation should be driven by blocking correctness and safety risk, not code taste

In `deep` mode:

- allow broader production concerns to surface when they are concrete and evidenced
- still skip pure style, micro-polish, and speculative future cleanup
- keep `P3` and `Nit` out unless they materially affect correctness, safety, or maintainability of the completed feature

## Output

Follow host or user review-output instructions first. Otherwise use `references/output-contract.md`.

For automation, `review-entrypoint.py --format json` emits context shaped by `references/review-context.schema.json`. Individual findings should follow `references/finding.schema.json` when machine-readable output is needed.

Keep the review concise. Prefer a few high-signal findings over a flood of low-value comments.

For `checkpoint` reviews:

- keep the answer short
- lead with findings only if there are real blocking issues
- if nothing core is wrong, say `No core correctness or safety issues found in the current diff.`
- do not add broad follow-up sections just to be thorough

For `deep` reviews:

- use the full review structure
- stay focused on material findings
- include broader production-readiness concerns when they are real and evidenced

For `final` reviews:

- use the full review structure
- include broader production-readiness concerns when they are real and evidenced
