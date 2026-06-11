# Security, Privacy, Performance, And Scalability Gates

Load this reference when code touches authentication, authorization, user input, files, databases, secrets, tokens, payments, PII, network calls, admin features, serialization, template rendering, shell commands, dependencies, hot paths, batch jobs, queues, caches, or rendering.

## Security And Privacy Gate

Check for concrete misuse paths:

- Authentication bypass
- Broken authorization or access control
- Insecure direct object reference
- Injection: SQL, command, template, LDAP, NoSQL, prompt, or header injection
- XSS, CSRF, SSRF, and open redirect risks
- Path traversal and unsafe file upload/download
- Secret, token, or PII leakage
- Sensitive information in logs, metrics, errors, traces, or analytics
- Unsafe deserialization
- Insecure defaults or missing deny-by-default behavior
- Missing audit trail for admin or security-sensitive actions
- Dependency or supply-chain risk introduced by the change

Security findings must include an attack or misuse path. Do not report broad security anxiety without a reachable path.

## Privacy Gate

Check:

- Data minimization
- User consent and purpose limitation when visible in product code
- Retention and deletion behavior
- PII propagation across logs, queues, caches, analytics, or third-party APIs
- Redaction in errors and support tooling
- Tenant or workspace isolation

## Performance And Scalability Gate

Run when code touches hot paths, loops over large data, database access, network calls, rendering, serialization, background jobs, queues, caches, batch processing, or startup.

Check:

- N+1 queries
- Unbounded loops or memory growth
- Missing pagination or streaming
- Missing indexes or inefficient query predicates
- Blocking operations in async paths
- Excessive retries or retry storms
- Cache correctness and invalidation
- Thundering herd risks
- Lock contention and shared mutable state
- Work done per request that should be amortized or precomputed
- Startup path regressions

Report performance issues only when plausible at realistic scale. Include the expected scale trigger and affected path.

## Operational Readiness Gate

Check:

- Can operators detect the failure?
- Can operators identify affected users, jobs, records, or requests?
- Is there enough context in logs without leaking sensitive data?
- Are metrics and alerts aligned with the failure mode?
- Is rollback or mitigation clear for risky changes?
