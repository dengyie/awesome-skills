# Design Rounds

Use this reference before broad website implementation.

Design rounds are workflow gates inside the current milestone. Milestone phases manage delivery and review scope; design rounds manage the order of design decisions, artifacts, implementation slices, and visual QA. Do not collapse the rounds into a single final checklist.

Each round must record:

- Entry Criteria
- Required Output
- Exit Criteria
- User Confirmation
- Round exit evidence
- Open blockers or accepted gaps

## Round 0: Context And Milestone

Entry Criteria:

- A website task is active.
- Project files, memory, and available visual assets have been inspected when present.

Required Output:

- milestone contract
- route inventory or explicit route assumptions
- P0/P1 scope, P2/P3 backlog, and Manual-required gaps
- source-path assumption: existing references, generated candidates, historical mockups, or framework-only

Exit Criteria:

- the current milestone is bounded
- the route matrix and strongest known visual sources are named
- broad design work has a documented target

User Confirmation:

- Required only when route scope, audience, brand, or final visual target is ambiguous.

## Round 1: Visual Direction Candidates

Entry Criteria:

- The site is from-zero, visually open, or lacks a binding route reference.
- Existing assets are not strong enough to skip candidate selection.

Required Output:

- 2-4 visual direction images, homepage mockups, or route mockups
- visual-source inventory entries for each candidate
- recommended direction with rationale when useful

Exit Criteria:

- user selects one direction, combines directions, or explicitly authorizes `Framework Ready` only
- selected direction is recorded before it becomes `approved-direction`, `binding-route`, or `temporary-binding`

User Confirmation:

- Required. Round 1 visual direction selection cannot be inferred from text mood words or agent preference.

## Round 2: Design System And Route Decomposition

Entry Criteria:

- A binding reference, selected direction, historical mock, or framework-only target exists.

Required Output:

- design-system baseline
- visual source map with authority status
- route-by-route decomposition of layout, typography, color, spacing, components, assets, interactions, and responsive behavior
- fidelity budget for binding routes

Exit Criteria:

- every core route has a source owner or explicit framework-only rationale
- binding routes have decomposed visual facts instead of vague style notes

User Confirmation:

- Required when decomposition changes the selected visual direction, drops a visible route, or downgrades a binding route to framework-only.

## Round 3: Implementation Map And Asset Plan

Entry Criteria:

- Round 2 outputs exist.

Required Output:

- implementation map from visual regions to routes, components, data, assets, and responsive behavior
- asset plan for generated, drawn, coded, sourced, or existing assets
- screenshot and QA evidence destinations
- route implementation order

Exit Criteria:

- broad implementation can start without inventing route structure from memory
- required asset gaps have planned create/source/generate actions

User Confirmation:

- Required when new image generation, web-sourced assets, paid assets, or major scope downgrades are introduced.

Do not start broad implementation before Round 3 exits.

## Round 4: Implementation Slice

Entry Criteria:

- Round 3 exits.
- The project has a runnable implementation path.

Required Output:

- first core route or vertical slice implemented as real DOM, components, text, controls, links, charts or diagrams, local assets, and responsive behavior
- build/typecheck result when available
- desktop and mobile screenshots for the slice

Exit Criteria:

- the slice runs in browser QA
- interaction and responsive basics are testable
- screenshot-as-page and palette-only shortcuts are absent

User Confirmation:

- Required when the slice visibly diverges from the selected direction or when the user asked to inspect design before full buildout.

## Round 5: Page Item Fidelity Fix Loop

Entry Criteria:

- At least one binding route or implementation slice exists.

Required Output:

- side-by-side screenshot comparison
- page-by-page, item-by-item fidelity audit
- blocking visual deviations and accepted gaps
- fixes for P0/P1 visual blockers
- fresh recheck evidence after fixes

Exit Criteria:

- required binding items are `matched` or `accepted-gap`
- no required item remains `not-checked`, `blocked`, or `weak`
- route readiness follows the weakest item status

User Confirmation:

- Required before accepting material visual gaps that remain visible in final delivery.

## Round 6: Final Delivery Gate

Entry Criteria:

- Required implementation and fidelity rounds have exited.

Required Output:

- final route evidence rows
- build/typecheck result
- browser QA evidence for required desktop and mobile viewports
- production review or phase-gate review result
- delivery summary with framework-ready versus visual-delivery-ready status

Exit Criteria:

- current milestone P0/P1 acceptance criteria pass
- remaining work is routed to backlog or Manual-required
- final claim does not exceed the weakest route and round evidence

User Confirmation:

- Required for external launch, deploy, publication, or acceptance of known material gaps.

## No-Skip Rules

- Do not skip Round 1 for from-zero or visually open work unless the milestone is explicitly `Framework Ready` only.
- Do not start broad implementation before Round 3 exits.
- Do not use Round 6 QA to invent missing Round 1-3 artifacts after the fact.
- Do not claim `Visual Delivery Ready` when any required round is skipped, unrecorded, or collapsed into one pass.
- Do not treat screenshots, build success, or a generic route smoke test as a substitute for round exit evidence.
- Do not proceed from a round with unresolved P0/P1 blockers unless the milestone is stopped with a manual-attention report.

## Round Status Labels

- `not-started`
- `in-progress`
- `blocked`
- `exited`
- `skipped-accepted`

Use `skipped-accepted` only when the milestone explicitly makes the round unnecessary and the reason is recorded.
