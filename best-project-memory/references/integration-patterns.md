# Integration Patterns

Use this file when another skill should consume or update the `best-project-memory` model.

## Minimal integration questions

Every integrating skill should answer:

1. What memory does it read before acting?
2. What memory does it update after meaningful work?
3. What actions, if any, does it trigger for promotion, compaction, or handoff?

## Pattern 1: Review-oriented skill

Good for:

- code review
- diff review
- architecture review

Typical behavior:

- read `project-state.md`
- read a relevant workstream if the change belongs to one
- optionally append a review session block

Avoid:

- writing directly to `decisions.md` unless the user has accepted the decision

## Pattern 2: Build or implementation skill

Good for:

- feature delivery
- docs updates
- project setup

Typical behavior:

- restore context from project state and todo
- update a local workstream for parallel efforts
- append a session log entry after meaningful progress
- refresh todo state

## Pattern 3: Design skill

Good for:

- design-system work
- planning-heavy implementation
- route or workflow design

Typical behavior:

- read `project-state.md`
- keep design work in a dedicated workstream
- promote important design choices into `decisions.md`
- generate a handoff when the design pause point matters

## Pattern 4: Long-running orchestration skill

Good for:

- release hardening
- migration programs
- multi-phase refactors

Typical behavior:

- use workstreams heavily
- generate snapshots for evidence
- compact history into phase summaries
- lint memory before signoff or handoff

## Integration level model

### Level 1: Read-only

Skill reads memory but does not update it by default.

### Level 2: Read + append

Skill reads memory and updates lightweight current-state or session objects.

### Level 3: Governance-aware

Skill can coordinate workstreams, snapshots, promoted decisions, and handoffs.

## Repository-specific suggestions

### `production-code-quality-review`

Recommended starting level:

- Level 1

Suggested use:

- read `project-state.md`
- read relevant workstream state for sensitive review context

### `zero-to-website-design`

Recommended starting level:

- Level 3

Suggested use:

- keep route or delivery work in a workstream
- promote key design decisions
- generate handoff packs for interrupted design or QA work
