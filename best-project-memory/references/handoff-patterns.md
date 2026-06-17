# Handoff Patterns

Use handoff files only when the next session benefits from a compact continuation pack that is smaller and more directive than the full memory set.

## When to create a handoff

- the work stops midstream
- another agent or collaborator will continue
- the project has multiple parallel tracks
- the next steps are specific and should not be rediscovered

## Handoff shape

Use this skeleton:

```md
# Handoff

## Objective
- ...

## Current State
- ...

## Read First
- `path/to/file`

## Exact Next Actions
- ...

## Blockers
- ...

## Validation To Run
- ...
```

## Good handoff traits

- names exact files to open first
- states what is already true
- lists the next three to five concrete actions
- mentions validation still required
- stays short enough to read in under two minutes

## Phase summaries vs handoffs

Use `phases/` when summarizing a milestone that may be referenced later.

Use `handoffs/` when the immediate goal is clean continuation by the next session.

## Naming

Prefer one of these formats:

- `YYYY-MM-DD-topic-handoff.md`
- `phase-001-topic.md`

Choose names that remain understandable outside the current chat.

## Script note

The V2 helper `scripts/generate_handoff.py` may assemble a handoff from:

- `project-state.md`
- `todo.md`
- an optional workstream file

It should still produce the same handoff shape and keep the result directive rather than verbose.
