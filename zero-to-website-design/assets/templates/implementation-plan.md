# Implementation Plan

## Summary

Describe the implementation phase and target outcome.

## Delivery State

- Milestone target:
- Current round:
- Round exit evidence:
- Skipped or accepted rounds:
- Weakest expected route status:
- Related workstream:
- Memory update plan:
- Decision promotion trigger:
- Handoff trigger:
- Accepted-gap policy:

## Scope

- In scope:
- Out of scope:

## Route Order

1. Route:
2. Route:
3. Route:

## Design Round State

| Round | Status | Required Output | Exit Evidence | Blockers Or Accepted Gaps |
| --- | --- | --- | --- | --- |
| Round 0: Context And Milestone |  |  |  |  |
| Round 1: Visual Direction Candidates |  |  |  |  |
| Round 2: Design System And Route Decomposition |  |  |  |  |
| Round 3: Implementation Map And Asset Plan |  |  |  |  |
| Round 4: Implementation Slice |  |  |  |  |
| Round 5: Page Item Fidelity Fix Loop |  |  |  |  |
| Round 6: Final Delivery Gate |  |  |  |  |

## Route Ownership And Risks

- Binding route owners:
- Temporary route owners:
- Route-owner risk:
- Upgrade or replacement triggers:

## Reference Fidelity Plan

- Reference decomposition:
- Reference-To-DOM Map:
- Fidelity budget:
- Blocking visual deviations:
- Accepted visual gaps:
- Resource-To-File Map:
- Generated UI asset prompts:
- Component-slot asset records:
- Implementation screenshot destinations:
- Side-by-side comparison destinations:
- Top 3 visible differences record:
- Fix loop owner:

## Reference-To-DOM Map

| Reference Region | DOM Component | Text Real DOM? | Asset Strategy | Interaction | Must Not Do |
| --- | --- | --- | --- | --- | --- |

Every visible binding-reference region must be mapped to real DOM/layout, CSS-drawn primitive, generated/local component-slot asset, or accepted gap before broad implementation.

## Resource-To-File Map

| Reference Region | Resource Unit | Unit Type | File Path | Owner Component | Reuse Scope | Split Reason | Must Stay Separate From | May Compose With | Text Policy | Edit Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Every generated, sourced, drawn, extracted, or local visual asset for a binding route must be mapped to an atomic resource unit, justified composite, CSS/DOM primitive, or accepted gap before asset creation. Split by edit, reuse, responsive, interaction, text, licensing, and replacement boundaries rather than visual proximity.

## Component-Slot Asset Records

| Route/Section | Resource Unit | Target Size Or Aspect Ratio | Reference Region | Must Match | Must Avoid | Split Reason | Text Policy | Perspective/Tilt Ownership | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Visual Asset Pipeline

| Route | Reference Region | Implementation Owner | Resource Unit | Asset Slot | Text Policy | Perspective/Tilt Policy | Evidence Path | Atomicity Status | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Implementation owner must be one of `dom-owner`, `css-owner`, `asset-owner`, or `accepted-gap`. Atomicity status must be `pass`, `accepted-gap`, `blocked-maintainability`, or `blocked-visual`. The route readiness claim follows the weakest visual asset pipeline status.

## Key Changes

- Design system:
- Components:
- Routes:
- Data/content:
- Assets:
- Metadata:

## Files

- Create:
- Modify:
- Preserve:

## QA Plan

- Build command:
- Route evidence destination:
- Desktop routes:
- Mobile routes:
- Interaction checks:
- Asset checks:
- Framework-ready check:
- Delivery-ready check:
- Reference fidelity check:
- Visual usability gate:
- First-viewport composition check:
- Blocking failure rule:

## Risks

- Risk:
- Mitigation:

## Done Criteria

- [ ] Design docs updated
- [ ] Implementation complete
- [ ] Build passes
- [ ] Browser QA passes
- [ ] Production review complete
- [ ] Known gaps recorded
- [ ] Memory/workstream state updated
