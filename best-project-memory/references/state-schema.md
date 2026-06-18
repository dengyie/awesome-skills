# State Schema

Use `.codex-memory/` as the repository-local memory root.

## Required files

### `project-state.md`

Purpose: the current operating panel for the project.

Recommended sections:

- `# Project State`
- `## Objective`
- `## Current Phase`
- `## Current Branch`
- `## Last Verified`
- `## Active Risks`
- `## Active Blockers`
- `## Current Focus`
- `## Next Milestone`
- `## Key Artifacts`

Rules:

- Keep this file short.
- Prefer bullets over long prose.
- Overwrite the live snapshot instead of appending session history here.

### `session-log.md`

Purpose: append-only record of meaningful work slices.

Use this entry shape:

```md
## YYYY-MM-DD HH:mm
- Task:
- Actions:
- Results:
- Next:
- Blockers:
```

Rules:

- Append new entries in chronological order.
- One entry can summarize a coherent work block.
- Avoid chat-like transcripts.

### `decisions.md`

Purpose: durable ADR-lite log for choices that future sessions should not rediscover.

Use this entry shape:

```md
## YYYY-MM-DD - Decision Title
- Decision:
- Rationale:
- Alternatives considered:
- Impact:
- Rollback trigger:
- Related files:
```

Rules:

- Capture why the choice was made.
- Add `Related files` or commits when known.
- Prefer one decision per entry.

### `todo.md`

Purpose: actionable queue for current work.

Use this structure:

```md
# TODO
## In Progress
- [ ] item
## Next
- [ ] item
## Done
- [x] item
```

Rules:

- Keep active sections short enough to scan quickly.
- Mark done items rather than deleting them.
- Remove obsolete items only when they were never actually started or were duplicated.

## Optional directories

### `phases/`

Purpose: milestone or phase summaries.

Suggested filename:

- `phase-001-discovery.md`
- `2026-06-17-release-hardening.md`

Include:

- phase goal
- outcomes
- open risks
- next entry condition

### `handoffs/`

Purpose: compact continuation packs for another session or collaborator.

Suggested filename:

- `2026-06-17-auth-refactor-handoff.md`

Include:

- current objective
- current state
- exact next actions
- blockers
- files to read first

### `workstreams/`

Purpose: bounded state for parallel or long-running subtracks.

Suggested filename:

- `release-hardening.md`
- `docs-refresh.md`
- `auth-refactor.md`

Recommended sections:

- `# Workstream`
- `## Objective`
- `## Current State`
- `## Blockers`
- `## Files`
- `## Next Actions`
- `## Validation`

Rules:

- keep local detail here instead of bloating `project-state.md`
- use one file per meaningful parallel effort
- use `references/workstream-template.md` when creating new workstreams manually

### `snapshots/`

Purpose: script-friendly evidence captures for branch, file, validation, or workstream state.

Suggested filename:

- `2026-06-17-branch-state.md`
- `2026-06-17-release-hardening.md`

Rules:

- prefer deterministic generation
- keep them evidentiary rather than narrative
- do not treat them as the sole human-facing status summary
- use `references/snapshot-schema.md` when defining or evolving snapshot content

## Encoding and maintenance

- Use UTF-8.
- Prefer stable headings so scripts can update predictable sections.
- Treat the repository copy as the source of truth when chat memory disagrees.
