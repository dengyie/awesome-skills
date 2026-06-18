# Surface Contract

Use this file to define the stable memory surface that other skills and helper scripts are allowed to rely on.

## Standard memory root

All project memory lives under:

```text
.codex-memory/
```

## Required top-level files

- `project-state.md`
- `todo.md`
- `decisions.md`
- `session-log.md`

These are the minimum continuity surface.

## Optional directories

- `phases/`
- `handoffs/`
- `workstreams/`
- `snapshots/`

Only create optional directories when the current project or workflow justifies them.

## Ownership model

### Human-summary dominant

These files are primarily semantic summaries written or curated by the agent:

- `project-state.md`
- `todo.md`
- `decisions.md`
- `handoffs/*.md`
- `phases/*.md`
- `workstreams/*.md`

Scripts may help populate them, but they should not silently replace high-level meaning with guessed prose.

### Script-evidence dominant

These objects may be owned mostly by deterministic helpers:

- `snapshots/*`

Snapshots are for evidence capture, structured context, and machine-friendly state, not final human narrative.

See:

- `references/workstream-template.md`
- `references/snapshot-schema.md`

### Append-heavy history

These files accept regular append operations and later compaction:

- `session-log.md`

## Scope rules

### Global scope

Use `project-state.md` and `todo.md` only for project-level truth:

- current objective
- current phase
- top risks or blockers
- highest-priority next actions

Do not turn them into detailed execution logs.

### Workstream scope

Use `workstreams/*.md` for bounded parallel efforts such as:

- release hardening
- auth refactor
- docs cleanup
- migration rollout

If a task has its own blockers, files, validation, or next actions, it likely belongs in a workstream file instead of the global state.

## Change policy

When changing the surface contract:

1. preserve backward readability where practical
2. update `state-schema.md` and any affected examples
3. update tests that assert the expected package structure
4. do not introduce new top-level objects casually

## Script write boundaries

Deterministic helpers may safely:

- initialize missing files and directories
- append session entries
- generate snapshots
- scaffold handoffs or workstream files

Deterministic helpers should be careful about:

- rewriting human-authored summaries
- merging conflicting semantic statements
- deleting historical content

Default rule: extract evidence automatically, but keep semantic judgment conservative.
