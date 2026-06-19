# Framework-First Delivery

Use this reference when the website structure should ship before all final content or final artwork is ready.

## Delivery Phases

Recommended phases:

1. brief and visual-source phase
2. design-doc phase
3. framework implementation phase
4. mock-asset integration phase
5. route QA phase
6. production hardening phase
7. publish or handoff phase

## Framework Ready

A route is `Framework Ready` when:

- the page shell exists
- header, navigation, footer, and core route hierarchy work
- major layout regions match the intended composition
- card, list, and detail systems exist
- typography hierarchy is coherent
- placeholder or `temporary-binding` assets are correctly placed
- temporary assets are documented with route ownership and replacement triggers
- responsive behavior is stable
- no overflow, clipping, or dead interactions remain
- the route composition is accepted even if final bespoke artwork is not ready yet
- from-zero visual direction selection is either recorded or explicitly listed as still open

## Visual Delivery Ready

A route is `Visual Delivery Ready` when:

- from-zero visual direction has been selected by the user when no stronger binding source existed
- the route matches its `binding-route` or approved `temporary-binding` references closely
- spacing, hierarchy, and emphasis are tuned
- asset quality is acceptable for delivery
- metadata and content framing are coherent
- any remaining temporary assets are explicitly acknowledged as post-pass gaps
- remaining differences are minor and explicitly documented

## Required Reporting

When a pass stops at framework-first delivery, say so clearly.

Report:

- which routes are only `Framework Ready`
- which assets remain temporary
- whether those assets control route composition or only slot/texture behavior
- what has to change before visual delivery signoff
- what QA evidence already exists

## Guardrails

- framework-first is a valid milestone, not a silent excuse for unfinished work
- provisional visuals must remain visible in docs and final reports
- production review still applies before claiming a delivery-ready state
