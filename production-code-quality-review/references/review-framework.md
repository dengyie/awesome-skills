# Review Framework

Use this reference for substantial reviews, cross-cutting changes, risky diffs, or architecture-sensitive work.

## Phase 0: Scope And Intent

Identify:

- What changed
- Intended behavior
- Affected modules and ownership boundaries
- External systems, APIs, databases, queues, caches, files, or users affected
- Whether the change is local, cross-cutting, or architectural
- Risk level: low, medium, high, or critical

Keep this mostly internal unless it materially affects the final recommendation.

## Phase 1: Correctness

Review:

- Control flow and branch behavior
- Data flow and state transitions
- Input/output behavior and return values
- Null, undefined, empty, zero, and missing-value handling
- Type assumptions and runtime validation
- API contracts and backward compatibility
- Database query correctness
- Serialization and deserialization
- Time, date, timezone, and ordering logic
- Race conditions in shared state or async code

Ask:

- Can valid input produce wrong output?
- Can invalid input break the code?
- Are errors swallowed?
- Are assumptions enforced?
- Does this break existing callers?
- Does similar functionality already exist and should it be reused?

## Phase 2: Robustness

Review behavior under failure, load, bad input, and real production conditions:

- Error handling and propagation
- Retry, timeout, and cancellation behavior
- Idempotency and duplicate requests
- Partial failure and transaction boundaries
- Resource cleanup for files, sockets, handles, and memory
- Concurrency safety and backpressure
- Rate limiting and fallback behavior
- Logging, metrics, traces, and alertability
- Sensitive information in logs

Ask:

- What happens when dependencies are slow or unavailable?
- What happens on duplicate requests?
- Can this create inconsistent state?
- Can this fail silently?
- Can operators debug the failure from logs or metrics?

## Phase 3: Architecture

Review:

- Module boundaries
- Dependency direction
- Coupling and cohesion
- Abstraction level
- Separation of concerns
- Ownership of business logic
- Framework leakage
- Domain model consistency
- API boundaries and data ownership
- Configuration strategy
- Reuse versus duplication
- Simplicity versus over-engineering

Report architecture issues only when they create real future cost, not because another design is possible.

## Phase 4: Evolution

Review:

- Extensibility and deleteability
- Migration and rollback path
- Feature toggle needs
- Backward compatibility
- Test and observability safety nets
- Documentation of non-obvious decisions
- Upgrade, downgrade, and vendor risks
- Schema evolution and API versioning

Ask:

- What happens when this feature grows by 2x?
- What happens when another team integrates with it?
- What will be hard to change six months from now?
- Is this shortcut becoming structural debt?

## Phase 5: Tests

Review tests as production code:

- Are tests added or updated for changed behavior?
- Would tests fail if the implementation is broken?
- Are edge cases and failure paths covered?
- Are integration points covered?
- Are concurrency or time-sensitive paths tested when relevant?
- Are mocks hiding real integration risk?
- Are snapshots too broad or too weak?
- Are tests deterministic and readable?

Do not simply say "add tests." Name the exact test scenario.

## Phase 6: Verification Pass

Before final output, classify every candidate finding:

- Confirmed: directly supported by code
- Likely: strongly implied but not fully proven
- Needs confirmation: possible issue requiring runtime or project context
- Removed: speculative or too minor

Only include confirmed and important likely findings in the main list. Move uncertain material to questions. Remove style-only opinions unless they affect maintainability.

## Final Recommendation Labels

Use one of:

- Safe to merge
- Safe to merge with follow-ups
- Fix P1/P0 issues before merge
- Do not merge yet

State the minimal required fixes.

## Final Output Structure

Use host or user review-output instructions first. If no stronger structure is provided, use this order:

1. Top findings ordered by severity
2. Questions or needs confirmation
3. Architecture assessment
4. Robustness assessment
5. Test assessment
6. Meaningful strengths observed
7. Final recommendation

For each finding, include:

- Severity and title
- Location with file and line when available
- Problem
- Why it matters
- Evidence
- Suggested fix

Keep summaries brief. Do not bury findings below general commentary.
