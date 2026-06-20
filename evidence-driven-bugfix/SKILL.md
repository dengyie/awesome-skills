---
name: evidence-driven-bugfix
description: Use when fixing any bug, test failure, or unexpected behavior that requires evidence-first diagnosis, failing evidence before implementation, fresh verification before any success claim, and continued looping until fixed or legally blocked.
---

# Evidence-Driven Bugfix

## Mission

Fix bugs through evidence, not guesses.

Do not implement fixes without failing evidence.
Do not claim success without fresh verification evidence.
Continue the loop until the bug is fixed or an evidence-backed legal exit applies.

## Iron Laws

```text
NO FIX WITHOUT FAILING EVIDENCE
NO ROOT-CAUSE GAP HIDDEN BY A SYMPTOM FIX
NO SUCCESS CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

## State Machine

Use this state machine:

```text
Investigating
  -> Reproduced
  -> Root-caused
  -> Fixing
  -> Verifying
  -> Fixed
```

Legal non-fixed exits:

- `Manual-required`
- `Proven-external-blocker`

State meanings:

- `Investigating`: logs, stack traces, code paths, recent changes, and runtime evidence are still being gathered or clarified.
- `Reproduced`: a stable failing evidence chain exists and can later be re-run or re-checked.
- `Root-caused`: a single root-cause hypothesis is supported by evidence strongly enough to justify a minimal fix.
- `Fixing`: a minimal root-cause fix is being implemented.
- `Verifying`: the same failing evidence chain is being re-run fresh to decide whether the bug is actually fixed.
- `Fixed`: only allowed when fresh verification evidence proves the original failure is gone.
- `Manual-required`: progress now depends on a human action, permission, credential, device, environment, or decision the current session cannot provide.
- `Proven-external-blocker`: evidence shows the unresolved blocker is outside the current code or control boundary and cannot be removed in the current session.

## Workflow

You are a replacement-grade primary bugfix workflow, not a loose debugging reference.

All bugfix work must pass through these six gates in order:

1. `Symptom Capture`
2. `Failing Evidence Gate`
3. `Root Cause Investigation`
4. `Minimal Fix Plan`
5. `Fresh Verification Gate`
6. `Truthful Completion Gate`

### Gate 1: Symptom Capture

Read `references/symptom-capture.md`.

Capture:

- the observed symptom
- the visible failure behavior
- the impact surface when known
- whether the evidence is directly observed or user-reported

Do not present guesses as facts.

### Gate 2: Failing Evidence Gate

Read `references/failing-evidence-gate.md` before any implementation starts.

Accepted failing evidence, in priority order:

1. automated failing test
2. failing repro script
3. stable reproduction steps
4. deterministic failing log or error response that can be re-checked against the same failing scenario

Screenshots and recordings may support symptom capture, but they cannot pass this gate by themselves.

No failing evidence means no implementation.

If evidence is incomplete, keep investigating. Do not move into a fix claim or a fix implementation state.
When a stable repro can reasonably be automated, convert it into a failing regression test before or alongside the fix.

### Gate 3: Root Cause Investigation

Read `references/root-cause-investigation.md` when the failure origin is unclear, the stack is deep, logs are incomplete, or multiple components may be involved.

You must:

- read the relevant logs and error output carefully
- inspect stack traces and nearby code
- check recent code, config, and environment changes
- trace data flow and call flow backward
- add diagnostic evidence at component boundaries when needed

Do not patch symptoms while the root cause remains unproven.

### Gate 4: Minimal Fix Plan

Read `references/minimal-fix-plan.md`.

Define:

- the suspected root cause
- why this is the fix layer
- the smallest acceptable change
- what is intentionally out of scope for this loop

Implement only one root-cause fix at a time.

### Gate 5: Fresh Verification Gate

Read `references/fresh-verification-gate.md` before making any status or success claim.

You must:

- rerun or recheck the same failing evidence chain captured earlier
- confirm that the original failure has turned green or disappeared as expected
- run the minimum necessary regression checks
- read the actual output rather than inferring results

When a stable repro was automatable, the fresh verification should prefer that automated regression test as the primary proof path.

If fresh verification fails, return to investigation or root-cause analysis and continue the loop.

### Gate 6: Truthful Completion Gate

Read `references/truthful-completion.md` before reporting completion, pause state, or blocker state.

Do not imply success, completion, or correctness without fresh verification evidence.

Only these terminal outcomes are allowed:

- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

## Loop Rule

Continue the loop until the bug is fixed or a legal exit applies.

The loop does not end merely because:

- a code change was made
- a hypothesis sounds plausible
- a partial check passed
- manual spot-checking looked better

If the bug is not fixed, continue the loop.

If fresh verification fails, return to investigation or root-cause analysis and continue the loop.

## Legal Exit Rules

Read `references/manual-required-and-external-blockers.md` before claiming a non-fixed terminal outcome.

Use `Manual-required` only when evidence shows progress now depends on:

- human approval or decision
- missing credentials or secrets
- device access
- account permissions
- an external setup step the current session cannot perform

Use `Proven-external-blocker` only when evidence shows:

- the unresolved cause is outside the current code or execution boundary, and
- the current session cannot remove it

Neither legal exit may be described as "fixed."

## Reference Routing

- Read `references/workflow-contract.md` to load the full state machine, gate sequence, and loop contract.
- Read `references/symptom-capture.md` before turning a vague report into a repair workflow.
- Read `references/failing-evidence-gate.md` before any implementation starts.
- Read `references/root-cause-investigation.md` when the failure origin is unclear or the system crosses multiple components.
- Read `references/minimal-fix-plan.md` before implementing changes.
- Read `references/fresh-verification-gate.md` before making any status or success claim.
- Read `references/truthful-completion.md` before reporting completion, pause state, or blocker state.
- Read `references/manual-required-and-external-blockers.md` before ending on a non-fixed status.
- Follow `references/output-contract.md` for the final user-facing report structure.

## Output Expectations

Use the output contract in `references/output-contract.md`.

At minimum report:

- current state
- symptom
- failing evidence
- root cause
- fix applied
- fresh verification
- outcome
- if not fixed, next loop or blocker
