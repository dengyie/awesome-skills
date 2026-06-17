# Project Memory Integration

Use this reference when `zero-to-website-design` is working inside a repository that uses `.codex-memory/`.

This package should behave as a Level 3 governance-aware consumer of `best-project-memory`.

## Read Order

Before major website work, read when present:

1. `.codex-memory/project-state.md`
2. `.codex-memory/todo.md`
3. the most relevant website workstream under `.codex-memory/workstreams/`
4. the latest relevant handoff when the work is being resumed

## Recommended Workstream Names

Use one bounded workstream when the website effort has its own blockers, files, QA state, or next actions.

Good defaults:

- `website-delivery.md`
- `route-framework.md`
- `mock-asset-pass.md`
- `visual-qa-pass.md`
- `launch-hardening.md`

Keep the slug tied to the current delivery slice, not to every tiny task.

## When To Update Memory

### Update `project-state.md`

Update when:

- the current website phase changes
- framework-ready or delivery-ready milestone status changes
- blockers or risks change
- the next milestone changes
- QA or production review materially changes release confidence

### Update `todo.md`

Update when:

- route, QA, or asset tasks move between in-progress, next, and done
- a new highest-priority website action becomes clear

### Append `session-log.md`

Append after meaningful progress such as:

- design docs materially updated
- a route group implemented
- mock-asset integration completed
- browser QA executed
- production review completed

Keep the entry grounded in:

- routes touched
- docs updated
- tests or build commands run
- QA status
- exact next action

### Update `workstreams/*.md`

Create or update a workstream when:

- website delivery spans multiple sessions
- framework implementation is separate from visual polish
- mock-asset integration becomes its own track
- QA or hardening has its own blockers

### Promote `decisions.md`

Promote a durable decision when:

- a visual authority becomes `binding-route`
- a `temporary-binding` strategy is accepted for a milestone
- a route structure, asset strategy, or content policy becomes binding
- a framework-first milestone is intentionally accepted

Use `best-project-memory/scripts/promote_decision.py` when possible.

### Generate handoff artifacts

Generate or update a handoff when:

- the work pauses midstream
- framework-ready routes still need asset upgrades
- QA uncovered follow-up issues for another session
- production review happened but delivery is not yet complete

Use `best-project-memory/scripts/generate_handoff.py` or `handoff_pack.py` when appropriate.

## Website-specific Summary Guidance

When summarizing website work in memory, prefer short bullets covering:

- current route or delivery phase
- binding or temporary visual sources in use
- framework-ready versus delivery-ready status
- QA state
- next action and blockers

## Guardrails

- do not dump route-level detail into `project-state.md` when it belongs in a workstream
- do not promote trivial implementation details into `decisions.md`
- do not skip handoff generation when another session would have to reconstruct route or QA state from chat alone
- do not let browser QA results live only in chat if they materially affect delivery
