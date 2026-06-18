---
name: best-project-memory
description: Use when restoring project context at the start of repo work, maintaining durable project memory across sessions, recording decisions, updating task state, preparing handoffs, or saving progress into repo-native memory files. Especially useful when users ask to continue previous work, save progress, summarize current state, capture decisions, or make another agent session resume cleanly.
---

# Best Project Memory

## Mission

Maintain a lightweight, repo-native continuity layer that another Codex session can reload quickly.

Prefer filesystem truth over chat memory. Keep the memory compact, current, and handoff-ready.

## Core Storage

Use `.codex-memory/` in the current repository root.

Always maintain these core files:

- `.codex-memory/project-state.md`
- `.codex-memory/session-log.md`
- `.codex-memory/decisions.md`
- `.codex-memory/todo.md`

Use these optional directories when the work justifies them:

- `.codex-memory/phases/`
- `.codex-memory/handoffs/`
- `.codex-memory/workstreams/`
- `.codex-memory/snapshots/`

Read `references/state-schema.md` before creating or restructuring the files.
Read `references/surface-contract.md` before changing the memory surface or deciding which objects are script-owned.

## Required Workflow

1. Restore context before project work.
   - Ensure `.codex-memory/` exists.
   - Read the four core files when they exist.
   - If phase or handoff docs exist and are obviously relevant, read only the needed ones.
   - Give a short loaded-context recap covering objective, phase, active TODOs, latest decisions, and blockers.

2. Keep the state panel current.
   - Treat `project-state.md` as the single current snapshot.
   - Overwrite only the live summary content there.
   - Keep it concise and operational.
   - Push workstream-level detail down into `workstreams/*.md` instead of bloating the global state.

3. Append session history.
   - Add a new entry to `session-log.md` after meaningful progress, at session close, or when the user asks to save progress.
   - Do not rewrite old session entries unless correcting obvious factual mistakes.

4. Record important decisions.
   - Add ADR-lite entries to `decisions.md` for meaningful choices, tradeoffs, or policy changes.
   - Include rationale and impact, not just the conclusion.

5. Maintain actionable TODO state.
   - Keep `todo.md` focused on active work.
   - Mark completed items done instead of deleting them.
   - Move stale or obsolete items only when their status is clear.

6. Create handoff artifacts when the work spans sessions or people.
   - Use `handoffs/` for compact continuation packs.
   - Use `phases/` for milestone summaries.
   - Use `workstreams/` for bounded parallel tracks inside larger projects.
   - Use `snapshots/` for machine-oriented evidence captures.
   - Read `references/handoff-patterns.md` before writing a new handoff file.

## Update Policy

Read `references/update-policy.md` before deciding where new information belongs.
Read `references/update-triggers.md` when deciding what kind of event should create a state update, promotion, or compaction step.

Use this routing rule:

- Current snapshot: `project-state.md`
- Time-ordered work record: `session-log.md`
- Durable choice with rationale: `decisions.md`
- Action queue: `todo.md`
- Milestone recap: `phases/*.md`
- Session transfer pack: `handoffs/*.md`
- Parallel task state: `workstreams/*.md`
- Evidence snapshot: `snapshots/*`

Do not dump everything into `session-log.md`.

## Deterministic Helpers

Use the helper scripts when they reduce repeated hand editing:

- `scripts/init_memory.py`: initialize `.codex-memory/` with the standard files and optional phase/handoff directories
- `scripts/append_session.py`: append a structured session entry to `session-log.md`
- `scripts/handoff_pack.py`: generate a compact handoff file from the current memory snapshot
- `scripts/compact_session.py`: compact older `session-log.md` history into a shorter summary and optional phase recap

Resolve script paths relative to this skill directory. For a user-scope install, they are usually under `$HOME/.agents/skills/best-project-memory/scripts/`.

## Reference Routing

- `references/state-schema.md`: read before creating or normalizing memory files
- `references/surface-contract.md`: read before changing structure, ownership, or script write boundaries
- `references/update-policy.md`: read before deciding what to update
- `references/update-triggers.md`: read when mapping work events to memory actions
- `references/quality-rules.md`: read when checking whether the memory has drifted into low-quality patterns
- `references/integration-patterns.md`: read when another skill should consume or update this memory model
- `references/examples.md`: read when you want concrete memory-entry examples
- `references/handoff-patterns.md`: read before writing handoff or phase summaries

Load only the references needed for the current task.

## Completion Standard

A project-memory pass is complete only when:

- the repo memory folder exists or has been intentionally confirmed unnecessary
- current objective, phase, blockers, and next step are easy to find
- durable decisions are captured with rationale
- TODOs reflect the real state of work
- another Codex session could resume without rereading the whole conversation
