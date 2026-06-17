# Snapshot Schema

Use snapshots for evidence-oriented state capture rather than human narrative.

## Purpose

Snapshots should capture deterministic or near-deterministic context such as:

- branch name
- changed files
- verification status
- relevant workstream state
- capture timestamp

## Suggested markdown shape

```md
# Snapshot

## Captured At
- 

## Branch
- 

## Changed Files
- 

## Validation State
- 

## Notes
- 
```

## Rules

- prefer machine-generated values where possible
- keep snapshots easy to regenerate
- do not use snapshots as the only human-facing project summary
- when a snapshot and a human summary disagree, inspect repo truth and resolve explicitly

## Script note

The V2 helper `scripts/snapshot_state.py` is expected to generate snapshots in this shape and may optionally sync a verification summary back into `project-state.md`.
