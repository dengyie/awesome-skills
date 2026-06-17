# Skill Matrix

Use this page when you want the fastest repository-level answer to: "Which skill should I use first?"

## Quick Matrix

| Skill | Best when you need | Core outputs | Common pairings | Avoid when |
| --- | --- | --- | --- | --- |
| `best-project-memory` | Continue work across sessions, keep durable project state, record decisions, and leave a handoff trail | `.codex-memory/` state, session logs, TODO updates, decision records, handoff artifacts | pairs naturally with both other shipped skills | the task is a one-shot edit with no continuity value |
| `production-code-quality-review` | Review a working tree, PR, or risky diff with production-engineering rigor | structured review context, review brief, merge-readiness findings, verification guidance | often paired with `best-project-memory` for long-running review tracks | the user wants implementation rather than review |
| `zero-to-website-design` | Turn a vague website brief or visual reference set into a documented, QA-checked delivery workflow | design docs, route plans, implementation map, visual provenance, browser QA artifacts | often paired with `best-project-memory`; may use `production-code-quality-review` before final signoff | the change is a small component tweak or backend-only task |

## Pick By Problem Type

Use `best-project-memory` first when the main problem is continuity:

- resume a repo after a pause
- save progress cleanly
- keep decisions and TODO state aligned with real work
- prepare another session to continue

Use `production-code-quality-review` first when the main problem is judgment about changed code:

- pre-merge review
- risky correctness check
- production readiness check
- diff triage with false-positive control

Use `zero-to-website-design` first when the main problem is designing and delivering a website:

- zero-to-one site work
- route-by-route website planning
- visual-reference-driven delivery
- browser QA before final signoff

## Pick By Expected Output

Choose `best-project-memory` when you want:

- updated `project-state.md`
- updated `todo.md`
- updated `session-log.md`
- recorded decisions and handoffs

Choose `production-code-quality-review` when you want:

- a review brief
- structured findings
- production-risk assessment
- verification commands

Choose `zero-to-website-design` when you want:

- design-system docs
- implementation plan
- page specs
- visual source map
- QA report or route evidence

## Common Pairings

`best-project-memory` + `production-code-quality-review`:

- long-running review cycles
- repeated follow-up fixes
- review notes that should update project continuity

`best-project-memory` + `zero-to-website-design`:

- multi-session website delivery
- route workstreams and design handoffs
- framework-ready versus delivery-ready milestone tracking

`production-code-quality-review` + `zero-to-website-design`:

- final website signoff
- production-oriented review after browser QA
- catching source-of-truth or delivery drift before publish

## Fast Routing Prompts

Use `best-project-memory`:

```text
Use $best-project-memory to restore this repo's current objective, decisions, active TODOs, and latest session summary before I continue.
```

Use `production-code-quality-review`:

```text
Use $production-code-quality-review to review this change for production correctness, robustness, and merge readiness.
```

Use `zero-to-website-design`:

```text
Use $zero-to-website-design to turn this website brief and reference set into design docs, implementation guidance, and browser QA.
```

## When Not To Use This Page

Skip the matrix and go straight to a package guide when you already know the skill you need:

- continuity and handoff: [`best-project-memory.md`](best-project-memory.md)
- production review: [`quickstart.md`](quickstart.md), [`review-workflows.md`](review-workflows.md)
- website delivery: [`zero-to-website-design.md`](zero-to-website-design.md)
