# Skill Matrix

Use this page when you want the fastest repository-level answer to: "Which skill should I use first?"

## Quick Matrix

| Skill | Best when you need | Core outputs | Common pairings | Avoid when |
| --- | --- | --- | --- | --- |
| `best-project-memory` | Continue work across sessions, keep durable project state, record decisions, and leave a handoff trail | `.codex-memory/` state, session logs, TODO updates, decision records, handoff artifacts | pairs naturally with every long-running shipped skill | the task is a one-shot edit with no continuity value |
| `evidence-driven-bugfix` | Run a disciplined bugfix workflow that requires failing evidence before implementation and fresh verification before any success claim | failing evidence, root cause, minimal fix, fresh verification result, truthful final status | pairs well with `best-project-memory` for long-running debugging and `production-code-quality-review` for checkpoint review after the fix | the user only wants a high-level review or a feature plan, not bugfix execution |
| `little-lighthouse-blog-publisher` | Publish, draft, update, or validate Little Lighthouse blog post packages | staged publishing plan, Markdown package, `.meta.json`, asset fallback summary, build/verifier/review/commit flow | pairs with `best-project-memory` for traceability and `production-code-quality-review` before commits | the target is not the Little Lighthouse blog or the user wants a browser CMS |
| `production-code-quality-review` | Review a working tree, PR, or risky diff with production-engineering rigor | structured review context, review brief, merge-readiness findings, verification guidance | often paired with `best-project-memory` for long-running review tracks | the user wants implementation rather than review |
| `split-image-assets` | Turn a source image into a reusable asset package with layers, masks, previews, metadata, and QA | transparent PNGs, masks, `background_clean.png`, `metadata.json`, `qa_report.md`, inspection previews | pairs with `zero-to-website-design` for website visuals and `production-code-quality-review` before publishing tooling changes | the user only wants a quick visual crop or expects deterministic scripts to perform segmentation |
| `zero-to-website-design` | Turn a vague website brief or visual reference set into a documented, QA-checked delivery workflow | design docs, route plans, implementation map, visual provenance, browser QA artifacts | often paired with `best-project-memory`; may use `production-code-quality-review` before final signoff | the change is a small component tweak or backend-only task |

## Pick By Problem Type

Use `best-project-memory` first when the main problem is continuity:

- resume a repo after a pause
- save progress cleanly
- keep decisions and TODO state aligned with real work
- prepare another session to continue

Use `evidence-driven-bugfix` first when the main problem is a bug that must be fixed truthfully:

- capture logs and failing evidence before coding
- trace root cause instead of patching symptoms
- verify the same failing signal turns green
- prevent "should be fixed" completion claims

Use `production-code-quality-review` first when the main problem is judgment about changed code:

- pre-merge review
- risky correctness check
- production readiness check
- diff triage with false-positive control

Use `split-image-assets` first when the main problem is making an image reusable:

- split source artwork into transparent object layers
- keep masks and cleaned backgrounds for later editing
- generate previews for edge and proportion inspection
- mark AI-assisted or uncertain regions for manual review

Use `little-lighthouse-blog-publisher` first when the main problem is publishing Little Lighthouse content:

- add a new Markdown article package
- prepare a draft-only post
- update blog metadata or article assets
- validate route, RSS, and sitemap inclusion before committing

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

Choose `evidence-driven-bugfix` when you want:

- a stable failing evidence chain
- a root-cause statement backed by logs or code evidence
- a minimal fix plan
- a fresh verification result
- a truthful fixed or blocked outcome

Choose `production-code-quality-review` when you want:

- a review brief
- structured findings
- production-risk assessment
- verification commands

Choose `little-lighthouse-blog-publisher` when you want:

- staged content intake
- title, slug, category, excerpt, and related-post suggestions
- asset fallback decisions
- build and `verify-blog-package` checks
- atomic blog publication commits

Choose `split-image-assets` when you want:

- transparent PNG object assets
- source-space masks
- cleaned background files
- `metadata.json`
- `qa_report.md`
- preview sprite sheets and checkerboard inspections

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

`best-project-memory` + `evidence-driven-bugfix`:

- long-running bug investigations
- multi-session reproduction and repair loops
- blocker tracking without false completion

`production-code-quality-review` + `evidence-driven-bugfix`:

- review after a fix lands
- checkpoint validation for risky bug repairs
- verifying that the fix diff did not introduce a new core regression

`best-project-memory` + `zero-to-website-design`:

- multi-session website delivery
- route workstreams and design handoffs
- framework-ready versus delivery-ready milestone tracking

`best-project-memory` + `little-lighthouse-blog-publisher`:

- long-running article drafting
- preserving publication decisions
- recording draft versus published follow-ups

`production-code-quality-review` + `zero-to-website-design`:

- final website signoff
- production-oriented review after browser QA
- catching source-of-truth or delivery drift before publish

`split-image-assets` + `zero-to-website-design`:

- turning generated or sourced website visuals into maintainable asset files
- keeping asset provenance, object boundaries, and QA evidence clear
- producing reusable UI, layout, animation, and compositing resources

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

Use `little-lighthouse-blog-publisher`:

```text
Use $little-lighthouse-blog-publisher to publish this Little Lighthouse Markdown draft as a blog post.
```

Use `evidence-driven-bugfix`:

```text
Use $evidence-driven-bugfix to fix this failure by first capturing logs, getting stable failing evidence, tracing the root cause, applying the minimal fix, and only reporting success after fresh verification.
```

Use `split-image-assets`:

```text
Use $split-image-assets to turn this source image into a reusable asset package with transparent PNGs, masks, metadata, previews, QA, and manual-review flags.
```

## When Not To Use This Page

Skip the matrix and go straight to a package guide when you already know the skill you need:

- continuity and handoff: [`best-project-memory.md`](best-project-memory.md)
- primary bugfix workflow: [`evidence-driven-bugfix.md`](evidence-driven-bugfix.md)
- Little Lighthouse blog publishing: [`little-lighthouse-blog-publisher.md`](little-lighthouse-blog-publisher.md)
- image asset splitting: [`split-image-assets.md`](split-image-assets.md)
- production review: [`quickstart.md`](quickstart.md), [`review-workflows.md`](review-workflows.md)
- website delivery: [`zero-to-website-design.md`](zero-to-website-design.md)

Repository-relative guide paths:

- `docs/usage/best-project-memory.md`
- `docs/usage/evidence-driven-bugfix.md`
- `docs/usage/little-lighthouse-blog-publisher.md`
- `docs/usage/split-image-assets.md`
- `docs/usage/zero-to-website-design.md`
