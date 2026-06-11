# Language And Stack Review Heuristics

Load this reference only for stacks present in the reviewed code. Prefer local project conventions over generic rules.

## TypeScript And JavaScript

- Check runtime validation at API and IO boundaries; TypeScript types do not protect runtime data.
- Watch for `any`, unsafe casts, optional chaining that hides missing state, and promise rejections.
- Check async control flow, cancellation, retries, and parallelism limits.
- Review package changes for transitive risk and bundle/runtime impact.
- For Node services, check resource cleanup, process-level error handling, and request-scoped context leakage.

## React And Frontend

- Check state ownership, effect dependencies, stale closures, and derived state duplication.
- Verify loading, empty, error, disabled, optimistic, and retry states.
- Check accessibility for interactive controls, labels, keyboard paths, and focus management.
- Watch for excessive rerenders, waterfall fetches, unbounded client data, and hydration mismatch risks.
- Review security for unsafe HTML, URL construction, auth state assumptions, and client-visible secrets.

## Python

- Check exception specificity, context preservation, and resource cleanup via context managers.
- Review mutable defaults, timezone handling, implicit `None`, and broad `except` blocks.
- For async code, verify awaited calls, cancellation behavior, timeouts, and blocking IO.
- For data code, check schema assumptions, precision, encoding, and deterministic ordering.

## Go

- Check error wrapping, ignored errors, context propagation, timeouts, and cancellation.
- Review goroutine lifecycle, channel closure, data races, and unbounded concurrency.
- Check pointer/nil behavior, zero values, and interface assumptions.
- Confirm tests cover table cases and failure branches.

## Java And JVM

- Check nullability boundaries, exception handling, transaction scope, and thread safety.
- Review dependency injection boundaries, service layering, and object lifecycle.
- Check serialization compatibility, migrations, and backward-compatible API evolution.
- Watch for blocking calls in reactive/async paths.

## Rust

- Check error modeling, ownership boundaries, lifetime-driven complexity, and `unwrap`/`expect` in production paths.
- Review concurrency primitives, lock scope, poisoning behavior, and async blocking.
- Check serialization compatibility and unsafe blocks for clear invariants.

## Databases

- Check transaction boundaries, isolation assumptions, migrations, indexes, locks, and rollback path.
- Review query cardinality, pagination, N+1 behavior, and tenant/workspace scoping.
- Verify migrations are backward compatible with rolling deploys when applicable.

## APIs And Integrations

- Check versioning, compatibility, idempotency, retries, timeouts, auth scopes, and error contracts.
- Confirm external failures do not corrupt local state.
- Review logging for correlation IDs and sensitive-data redaction.
