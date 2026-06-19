# Truthful Completion

## Purpose

Prevent false completion claims.

## Required Inputs

Before reporting completion, pause state, or blocker state, confirm:

- the current workflow state
- the latest failing evidence
- the latest fresh verification result
- whether the result is `Fixed`, `Manual-required`, or `Proven-external-blocker`

## Forbidden Completion Language

Do not say:

- "should be fixed"
- "probably solved"
- "looks good"
- "done"

unless fresh verification evidence has already proven the original failure is gone.

## Prohibited Shortcuts

Do not:

- imply success because a fix was attempted
- imply success because symptoms changed
- hide a blocker behind optimistic language

## Pass Condition

The reported outcome matches the evidence and does not imply success unless success has been freshly verified.
