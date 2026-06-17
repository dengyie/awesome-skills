# Best Project Memory

`best-project-memory` is the repository's continuity skill for durable project state, decision capture, and handoff-ready memory files.

## When to use it

Use it when you need to:

- continue previous repo work without rereading the whole conversation
- save progress at the end of a work block
- capture durable decisions and their rationale
- keep TODO state aligned with real work
- prepare a compact handoff for the next session

## What it manages

The skill uses `.codex-memory/` in the repo root.

Core files:

- `project-state.md`
- `session-log.md`
- `decisions.md`
- `todo.md`

Optional directories:

- `phases/`
- `handoffs/`
- `workstreams/`
- `snapshots/`

## Main workflow

1. Restore context.
   - Read the memory files.
   - Summarize objective, phase, blockers, and next actions.

2. Do the project work.
   - Keep the state current while the repo changes.

3. Save continuity.
   - Update the current snapshot.
   - Append a session log entry.
   - Record durable decisions.
   - Refresh TODO state.

4. Split parallel work when needed.
   - Use `workstreams/` for bounded streams inside larger projects.
   - Use `snapshots/` for evidence-oriented state capture.

## Helper scripts

Initialize the memory structure:

```bash
python3 best-project-memory/scripts/init_memory.py --repo .
```

Initialize the core files plus optional phase/handoff directories:

```bash
python3 best-project-memory/scripts/init_memory.py --repo . --with-optional-dirs
```

Initialize the full V2 governance surface with a starter workstream and snapshot:

```bash
python3 best-project-memory/scripts/init_memory.py \
  --repo . \
  --with-governance-dirs \
  --default-workstream "release hardening" \
  --default-snapshot
```

Repair a partial `.codex-memory/` layout without overwriting existing files:

```bash
python3 best-project-memory/scripts/init_memory.py \
  --repo . \
  --repair \
  --default-workstream "release hardening" \
  --default-snapshot
```

`--repair` restores missing core files and governance directories, and can also backfill a starter workstream or snapshot when those flags are provided. Existing non-missing files stay untouched.

Append a structured session entry:

```bash
python3 best-project-memory/scripts/append_session.py \
  --repo . \
  --task "Package the skill" \
  --actions "Added references, scripts, and tests" \
  --results "Skill validates and tests pass" \
  --next "Update usage docs"
```

Generate a handoff file:

```bash
python3 best-project-memory/scripts/handoff_pack.py \
  --repo . \
  --slug memory-upgrade \
  --objective "Finish the continuity skill polish" \
  --current-state "Package is implemented and tested." \
  --read-first best-project-memory/SKILL.md docs/best-project-memory-expansion-design.md \
  --next-actions "Review README wording" "Prepare release notes"
```

Generate a handoff from current project state and a workstream:

```bash
python3 best-project-memory/scripts/generate_handoff.py \
  --repo . \
  --slug release-hardening \
  --workstream "release hardening"
```

Capture an evidence snapshot and sync it back into `project-state.md`:

```bash
python3 best-project-memory/scripts/snapshot_state.py \
  --repo . \
  --slug working-tree \
  --validation-state "unit tests passing" \
  --notes "Captured after docs and script updates." \
  --write-project-state
```

Create or refresh a workstream file:

```bash
python3 best-project-memory/scripts/sync_workstream.py \
  --repo . \
  --slug "release hardening" \
  --objective "Stabilize package output" \
  --current-state "Tests are passing and docs are in progress." \
  --files README.md best-project-memory/SKILL.md \
  --next-actions "Run full review" "Prepare release notes" \
  --validation "unit tests passing"
```

Promote a durable decision into `decisions.md`:

```bash
python3 best-project-memory/scripts/promote_decision.py \
  --repo . \
  --title "Use workstreams for parallel release tracks" \
  --decision "Store parallel release state in workstream files." \
  --rationale "Global project state should remain compact." \
  --impact "Release coordination becomes easier to scan."
```

Run a structural lint pass on `.codex-memory`:

```bash
python3 best-project-memory/scripts/memory_lint.py --repo .
```

The lint pass now also flags:

- missing snapshot files still referenced by `project-state.md`
- long structured `session-log.md` history that should likely be compacted
- latest snapshot evidence with changed files that is not reflected in `project-state.md`

Check whether active TODO items have gone stale or vague:

```bash
python3 best-project-memory/scripts/stale_todo_check.py --repo .
```

The stale TODO check now fails when:

- an active item is too vague to act on
- an active item already appears in `## Done`
- active TODO state conflicts with recent session-history `Next:` evidence and a matching done item

Compact older session history while keeping the newest entries in place:

```bash
python3 best-project-memory/scripts/compact_session.py \
  --repo . \
  --keep-last 3 \
  --max-entries 6 \
  --phase-slug release-hardening \
  --title "Release hardening history"
```

`production-code-quality-review` can also act as an opt-in Level 2 consumer:

- keep the existing read-only review setup
- append a structured review session summary into `session-log.md`
- merge explicit review follow-up items into `todo.md`

Shipped integration levels in this repository today:

- Level 1: `production-code-quality-review` reads project memory and relevant workstreams into review context
- Level 2: `production-code-quality-review` can opt in to append review sessions and merge follow-up TODO items
- Level 2 hardening: explicit `P1:`, `Blocker:`, and `Urgent:` follow-ups route into `## In Progress`, while normalized duplicates are skipped across active TODO sections
- Level 3: `zero-to-website-design` uses workstreams, session continuity, delivery-state templates, and handoff-oriented project memory behavior

## Package contents

- `best-project-memory/SKILL.md`
- `best-project-memory/references/state-schema.md`
- `best-project-memory/references/update-policy.md`
- `best-project-memory/references/examples.md`
- `best-project-memory/references/handoff-patterns.md`
- `best-project-memory/references/workstream-template.md`
- `best-project-memory/references/snapshot-schema.md`
- `best-project-memory/scripts/init_memory.py`
- `best-project-memory/scripts/append_session.py`
- `best-project-memory/scripts/handoff_pack.py`
- `best-project-memory/scripts/snapshot_state.py`
- `best-project-memory/scripts/sync_workstream.py`
- `best-project-memory/scripts/generate_handoff.py`
- `best-project-memory/scripts/promote_decision.py`
- `best-project-memory/scripts/compact_session.py`
- `best-project-memory/scripts/memory_lint.py`
- `best-project-memory/scripts/stale_todo_check.py`

## Verification

Run the package tests:

```bash
python -m unittest discover best-project-memory/tests -v
```
