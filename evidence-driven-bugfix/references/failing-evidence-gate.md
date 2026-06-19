# Failing Evidence Gate

## Purpose

Require a reusable failure signal before implementation begins.

## Accepted Evidence

Use the strongest available evidence:

1. automated failing test
2. failing repro script
3. stable reproduction steps
4. deterministic failing log, error response, screenshot, or recording

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
