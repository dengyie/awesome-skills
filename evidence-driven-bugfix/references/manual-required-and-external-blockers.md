# Manual-Required And External Blockers

## Purpose

Define the only legal non-fixed exits.

## Manual-required

Use only when evidence shows progress now depends on something the current session cannot provide, such as:

- human approval or decision
- missing credentials or secrets
- device access
- account permissions
- an external setup step owned by a human

## Proven-external-blocker

Use only when evidence shows:

- the unresolved cause is outside the current code or execution boundary, and
- the current session cannot remove it

## Prohibited Shortcuts

Do not:

- use these states to avoid continued debugging
- use them without explicit evidence
- describe either state as fixed

## Pass Condition

The non-fixed terminal state is supported by evidence and described without implying success.
