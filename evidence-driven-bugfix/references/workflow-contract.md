# Workflow Contract

## Purpose

Define the full execution contract for `evidence-driven-bugfix`.

This workflow is responsible for:

- capturing the symptom truthfully
- securing failing evidence before implementation
- promoting a stable automatable repro into a failing regression test when feasible
- proving root cause before repair
- applying a minimal fix
- rerunning fresh verification
- continuing the loop until the bug is fixed or a legal exit applies

## State Machine

Use these states:

- `Investigating`
- `Reproduced`
- `Root-caused`
- `Fixing`
- `Verifying`
- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

## Gate Order

All work flows through these gates in order:

1. `Symptom Capture`
2. `Failing Evidence Gate`
3. `Root Cause Investigation`
4. `Minimal Fix Plan`
5. `Fresh Verification Gate`
6. `Truthful Completion Gate`

## Loop Rule

If the original failing evidence has not turned green, the loop is not complete.

Return to investigation or root-cause analysis whenever:

- fresh verification still fails
- a fix attempt changes symptoms without clearing the original failure
- new evidence weakens the current root-cause hypothesis

## Terminal Outcomes

Only these outcomes may end the loop:

- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

Anything else returns the workflow to investigation, evidence gathering, or root-cause analysis.

## Prohibited Shortcuts

Do not:

- implement without failing evidence
- treat screenshots or recordings alone as gate-passing evidence
- patch symptoms while the root cause remains unproven
- treat a code diff as evidence of success
- imply completion without fresh verification evidence
- stop only because the work feels close enough
