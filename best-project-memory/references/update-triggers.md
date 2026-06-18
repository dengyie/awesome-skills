# Update Triggers

Use this file to map project events to the correct memory action.

## Restore triggers

### Starting repo work

Read:

- `project-state.md`
- `todo.md`
- relevant `workstreams/*.md`
- latest `handoffs/*.md` only when obviously relevant

Action:

- produce a short loaded-context summary before major project work

## Current-state triggers

### Objective changed

Update:

- `project-state.md`

### Phase changed

Update:

- `project-state.md`
- `phases/*.md` if a milestone closed

### New blocker or risk appeared

Update:

- `project-state.md`
- relevant `workstreams/*.md` if the blocker is local to that stream

## Execution-history triggers

### Meaningful work block completed

Update:

- `session-log.md`

### User asked to save progress

Update:

- `session-log.md`
- `todo.md`
- `project-state.md` if the current snapshot changed

## Decision triggers

### Durable tradeoff chosen

Update:

- `decisions.md`

Examples:

- architecture choice became binding
- workflow or repo convention changed
- rollback condition was defined

## Workstream triggers

### Parallel task emerged

Create or update:

- `workstreams/<slug>.md`

Use when a task has its own:

- focus
- blockers
- touched files
- validation
- next actions

## Handoff triggers

### Work pauses midstream

Create or update:

- `handoffs/*.md`

Use especially when another session must continue without reading the full chat.

## Compaction triggers

### Session history becoming noisy

Promote or compact into:

- `phases/*.md`
- handoff summaries
- a compacted session summary when implemented

Compaction should preserve continuity while reducing reading cost.

## Snapshot triggers

### Evidence capture needed

Create or update:

- `snapshots/*`

Examples:

- branch and changed-file snapshot
- validation-state snapshot
- workstream evidence bundle

## Conflict triggers

### Memory disagrees with repo reality

Resolve by:

1. checking repository truth first
2. inspecting git state, files, or validation outputs
3. correcting the affected memory objects
