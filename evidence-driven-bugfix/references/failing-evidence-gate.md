# Failing Evidence Gate

## Purpose

Require a reusable failure signal before implementation begins.

## Accepted Evidence

Use the strongest available evidence:

1. automated failing test
2. failing repro script
3. stable reproduction steps
4. deterministic failing log or error response that can be checked again against the same scenario

The gate requires a replayable or re-checkable failure signal.
Screenshots or recordings alone are supporting context, not failing evidence by themselves.

## Required Inputs

You need:

- one concrete failure signal
- enough detail to rerun or re-check the same signal later

## Prohibited Shortcuts

Do not:

- implement code without a failure signal
- treat vague user belief as failing evidence
- treat stale evidence as current evidence

## Pass Condition

A clear failing evidence chain exists and can later be re-run or re-checked to prove the fix.
When that chain can reasonably become an automated test, prefer promoting it into a failing regression test before or alongside implementation.
