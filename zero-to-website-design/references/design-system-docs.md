# Design-System Docs

Use this reference before writing code for a zero-to-website project.

## Required Docs

Create or update equivalent project docs:

- `design-system/MASTER.md`
- `design-system/IMPLEMENTATION-PLAN.md`
- `design-system/ASSET-AND-DATA-SPEC.md`
- `design-system/VISUAL-SOURCE-MAP.md`
- `design-system/pages/<route>.md`

Use the templates in `assets/templates/` when the project has no stronger format.

Treat these documents as a pre-code gate for broad implementation. Do not jump from a loose brief or image set into route-wide editing until the equivalent artifact chain exists.

## MASTER.md Should Define

- project objective
- intake source or assumption basis
- brand/name
- audience
- route inventory and intentionally deferred routes
- current source-path choice
- milestone target
- visual principles
- typography hierarchy
- color tokens
- layout primitives
- component patterns
- interaction style
- accessibility rules
- responsive rules
- non-negotiables

## IMPLEMENTATION-PLAN.md Should Define

- phases
- route order
- route coverage for the current pass
- files likely to change
- data/content strategy
- asset strategy
- verification destinations
- QA gates
- deployment gate
- risks and assumptions

## ASSET-AND-DATA-SPEC.md Should Define

- content sources
- content source status by route family
- placeholder vs production content policy
- placeholder replacement conditions
- image/illustration sources
- icon and ornament strategy
- data ownership
- route-family ownership
- metadata ownership
- metadata, sitemap, RSS, or SEO requirements

## Page Specs Should Define

- route purpose
- binding visual references
- route status target
- desktop layout regions
- mobile layout behavior
- components
- content needs
- states and interactions
- acceptance checklist

## Design Docs Gate

Do not begin broad implementation until the docs answer:

- what site is being built
- what the compact intake output or equivalent assumptions are
- what visual references control it
- what routes are in scope
- what routes are intentionally deferred
- what milestone the current pass targets
- what assets are needed
- what content source classes are currently allowed
- what implementation order is expected
- how completion will be judged

For touched core routes, the gate should also make it easy to find:

- the relevant page spec or equivalent route doc
- the source-path summary
- the implementation plan
- the verification destination for route evidence
