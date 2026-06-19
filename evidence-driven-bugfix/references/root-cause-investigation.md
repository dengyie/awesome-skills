# Root Cause Investigation

## Purpose

Find the actual source of failure instead of patching symptoms.

## Required Inputs

Use:

- relevant logs and error output
- stack traces and nearby code
- recent code, config, and environment changes
- backward tracing through data flow and call flow

When evidence is incomplete across components, add diagnostics at component boundaries.

## Prohibited Shortcuts

Do not:

- patch symptoms while the cause is still ambiguous
- run multiple guess-fixes in parallel
- say "it's probably X" without evidence

## Pass Condition

A single root-cause hypothesis can be stated and supported by evidence strongly enough to justify a minimal fix.
