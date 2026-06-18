# Quality Rules

Use this file to recognize high-quality memory and detect drift early.

## High-quality current state

`project-state.md` is high quality when:

- the objective is explicit
- the current phase is current
- risks and blockers are easy to scan
- the next milestone is concrete
- it stays short enough to read quickly

Bad smell:

- it reads like a diary

Fix:

- move execution detail to `session-log.md` or a workstream file

## High-quality TODO state

`todo.md` is high quality when:

- every item is actionable
- active work is separated from done work
- stale work is visible instead of silently accumulating

Bad smells:

- vague items like "keep improving this"
- too many active items
- completed work mixed into active sections

Fix:

- rewrite items into concrete actions
- move lower-priority work out of `In Progress`

## High-quality decisions

`decisions.md` is high quality when:

- each decision has rationale
- impact is explicit
- repeated rediscovery is avoided

Bad smells:

- only the conclusion is written
- rationale is missing
- the same choice appears in many entries

Fix:

- promote one durable entry with rationale and related files

## High-quality session history

`session-log.md` is high quality when:

- entries summarize coherent work blocks
- results and next actions are both present
- long history remains compactable

Bad smells:

- transcript-like narration
- command dumps
- no clear next action

Fix:

- rewrite entries as compact summaries
- promote enduring knowledge into decisions or phases

## High-quality handoffs

`handoffs/*.md` are high quality when:

- the objective is explicit
- the current state is trustworthy
- read-first files are named
- next actions are executable

Bad smells:

- "continue from here" with no specifics
- no validation notes
- generic summaries that do not help the next session act

Fix:

- add concrete next actions and validation expectations

## High-quality workstreams

`workstreams/*.md` are high quality when:

- the stream has a clear purpose
- blockers, files, validation, and next actions stay local
- the global state does not duplicate every detail

Bad smells:

- the workstream repeats all of `project-state.md`
- the workstream never changes while its TODOs remain active

Fix:

- keep local detail in the workstream
- keep the global layer summarized

## High-quality snapshots

`snapshots/*` are high quality when:

- they capture evidence cleanly
- they do not pretend to be the final semantic truth
- they are easy to regenerate

Bad smell:

- using snapshots as the only human-readable narrative

Fix:

- keep snapshots evidentiary and project-state semantic

## Script note

V2 quality checks should be enforced by:

- `scripts/memory_lint.py`
- `scripts/stale_todo_check.py`

These scripts should catch obvious structural and actionability regressions before handoff, review, or release-style milestones.
