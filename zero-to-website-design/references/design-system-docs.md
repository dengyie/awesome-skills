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

## MASTER.md Should Define

- project objective
- brand/name
- audience
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
- files likely to change
- data/content strategy
- asset strategy
- QA gates
- deployment gate
- risks and assumptions

## ASSET-AND-DATA-SPEC.md Should Define

- content sources
- placeholder vs production content policy
- image/illustration sources
- icon and ornament strategy
- data ownership
- metadata, sitemap, RSS, or SEO requirements

## Page Specs Should Define

- route purpose
- binding visual references
- desktop layout regions
- mobile layout behavior
- components
- content needs
- states and interactions
- acceptance checklist

## Design Docs Gate

Do not begin broad implementation until the docs answer:

- what site is being built
- what visual references control it
- what routes are in scope
- what assets are needed
- how completion will be judged

