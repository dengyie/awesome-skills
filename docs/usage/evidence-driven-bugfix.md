# Evidence-Driven Bugfix

Use `evidence-driven-bugfix` when you want a primary bugfix workflow that refuses guess-fixes and refuses to declare success without fresh evidence.

It is the right skill when the main job is not "review this diff" but:

- inspect logs and code first
- secure failing evidence before implementation
- trace to root cause before fixing
- apply a minimal root-cause fix
- rerun fresh verification
- keep looping until the bug is fixed or a legal blocker is proven

## Best Fit

Use this skill for:

- test failures that need a full root-cause-to-fix loop
- production bugs with real logs or runtime evidence
- flaky or intermittent behavior once you can capture stable failing evidence
- integration issues where a code change alone is not proof of success
- bugfix sessions where false completion claims have caused rework before

Avoid this skill when:

- you only want a code review and not bugfix execution
- you only need a narrow API lookup
- the task is a new feature with no failure to investigate yet

## The Six Gates

Every bugfix runs through these gates:

1. `Symptom Capture`
2. `Failing Evidence Gate`
3. `Root Cause Investigation`
4. `Minimal Fix Plan`
5. `Fresh Verification Gate`
6. `Truthful Completion Gate`

This means the skill does not accept:

- "it probably broke here"
- "I changed the likely spot"
- "looks fixed now"
- "done, try it again"

without fresh evidence.

## Accepted Failing Evidence

The skill prefers the strongest evidence available:

1. automated failing test
2. failing repro script
3. stable reproduction steps
4. deterministic failing log, error response, screenshot, or recording

If no failing evidence exists yet, the workflow stays in investigation. It does not move into implementation.

## Allowed Outcomes

Only these terminal outcomes are allowed:

- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

`Manual-required` means the current session is blocked on a human decision, permission, credential, device, or external setup step.

`Proven-external-blocker` means the remaining blocker has been evidenced as outside the current code or execution boundary and cannot be removed in the current session.

Neither non-fixed outcome may be reported as a successful repair.

## Forbidden Completion Language

Do not use:

- "should be fixed"
- "probably solved"
- "looks good"
- "done"

unless fresh verification evidence already proves the original failure is gone.

## Example Prompt

```text
Use $evidence-driven-bugfix to fix this failure by first capturing logs, getting stable failing evidence, tracing the root cause, applying the minimal fix, and only reporting success after fresh verification.
```

## Expected Output Shape

The final report should at minimum include:

- `Current state`
- `Symptom`
- `Failing evidence`
- `Root cause`
- `Fix applied`
- `Fresh verification`
- `Outcome`
- `If not fixed, next loop or blocker`
