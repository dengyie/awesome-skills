# Update Policy

Use this file to decide what to write, where to write it, and when to leave history alone.

## Routing rules

### Write to `project-state.md` when

- the current objective changed
- the phase changed
- blockers or risks changed
- the next milestone changed
- verification status changed

Do:

- keep only the latest state
- rewrite the current summary for clarity

Do not:

- append time-series notes
- record every command or tiny step

### Write to `session-log.md` when

- meaningful progress happened
- the user asked to save progress
- a work block ended
- a blocker was discovered or cleared

Do:

- summarize the task, actions, results, and next step
- keep the entry grounded in observable work

Do not:

- paste raw terminal output unless very short and essential
- turn it into a chat transcript

### Write to `decisions.md` when

- a tradeoff was made
- a workflow or architecture choice became binding
- a team policy or repo convention was chosen
- a future session would ask "why did we do it this way?"

Do:

- name the decision clearly
- capture rationale and impact
- mention alternatives when relevant

Do not:

- log trivial implementation details
- duplicate the same decision in multiple entries

The V2 helper `scripts/promote_decision.py` should be used when a decision has clearly crossed from session detail into durable project knowledge.

### Write to `todo.md` when

- work items changed state
- a new next action became clear
- done items should be preserved for continuity

Do:

- keep the list actionable
- move work between `In Progress`, `Next`, and `Done`

Do not:

- leave stale checked-off items mixed with active work without sectioning

### Write to `phases/` when

- a milestone closed
- a workstream changed shape
- the project needs a durable summary bigger than a session log entry

### Write to `handoffs/` when

- another session must resume cleanly
- the user asks for a handoff
- the work is paused midstream with specific next actions

## Evidence policy

When available, tie memory updates to evidence:

- files changed
- tests run
- branches
- commits
- issue or PR identifiers

Keep the memory concise even when evidence is rich. Prefer links, paths, and short bullets over pasted output.

## Conflict policy

When filesystem memory and chat memory disagree:

1. trust repository files first
2. inspect actual code or git state if needed
3. update the memory files to resolve the discrepancy

## Cleanup policy

- Do not delete session or decision history unless the user explicitly asks.
- Compress by summarizing into phase docs, not by erasing history.
- Reword unclear current-state sections freely if the meaning stays accurate.
