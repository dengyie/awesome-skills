# QA Report

## Build

- Command:
- Result:
- Notes:

## Delivery State

- Framework-ready or delivery-ready:
- Current design round:
- Required rounds complete:
- Skipped or accepted rounds:
- Temporary-binding assets still in use:
- Handoff needed:
- Next-session follow-up:
- Overall route evidence status:

## Route Evidence

| Route | Route Type | Source Owner | Viewports Checked | Evidence | Status | Blocking Failures | Accepted Gaps | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Design Round Evidence

| Round | Status | Exit Evidence | Remaining Blockers | Accepted Gaps |
| --- | --- | --- | --- | --- |

Skipped or collapsed required rounds block final delivery unless the milestone records an explicit `skipped-accepted` reason.

## Reference Fidelity

| Route | Reference Screenshot | Implementation Screenshot | Side-by-side comparison | Top 3 Visible Differences | Fidelity Status | Blocking visual deviations | Accepted visual gaps | Next fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Reference-To-DOM Map Check

| Route | Reference Region | DOM Component | Text Real DOM? | Asset Strategy | Interaction | Must Not Do | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

No visible binding-reference region may remain `visual memory only`.

## Component-Slot Asset Records

| Route/Section | Resource Unit | Target Size Or Aspect Ratio | Reference Region | Must Match | Must Avoid | Split Reason | Text Policy | Perspective/Tilt Ownership | Output Path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Allowed component-slot raster assets do not carry full-route layout, readable text, navigation, or core controls.

## Resource Atomicity Check

| Route | Reference Region | Resource Unit | Unit Type | File Path | Owner Component | Split Reason | Must Stay Separate From | Composite Reason | Atomicity Status | Fix Or Accepted Gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Atomicity status must be one of `pass`, `blocked-maintainability`, `blocked-visual`, or `accepted-gap`.
Files that bake together multiple independent cards, icons, labels, controls, ornaments, panels, textures, diagram layers, or responsive units are `blocked-maintainability` until split or explicitly accepted.
Full-route screenshots, sliced route mockups, and layout-bearing raster shortcuts are `blocked-visual`.

## Visual Asset Evidence

| Route | Asset Slot | Resource Unit | Output Path | Source Method | Evidence Screenshot | Text Policy Pass | Perspective Policy Pass | Atomicity Pass | Replacement Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Final route readiness follows the weakest visual asset evidence status.

## First-Viewport Composition

| Route | Binding Reference Viewport | Implementation Viewport | Dominant Visual System | Primary Content Position | Next-Section Exposure | Lower Sections Compete With Hero? | Decorative Sections Push Content Down? | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Page Item Fidelity Audit

| Route | Viewport | Design Item | Reference Region | Implementation Region | Evidence Quality | Match Status | Deviation | Severity | Fix Action | Recheck Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Required binding-route items must be `matched` or `accepted-gap` before `Visual Delivery Ready`.
Unresolved `not-checked` or `blocked` items prevent visual delivery signoff.
Rows with `weak` evidence quality do not support visual delivery signoff.
Fixed rows must include fresh recheck evidence.

Full-page screenshot implementation check:
- Is any binding route primarily rendered from the whole reference screenshot:
- Are any links or actions transparent hotspots over that screenshot:
- If yes, status is blocked until the route is rebuilt as real DOM/components/assets/interactions:

## Interaction Checks

- [ ] Navigation links
- [ ] Primary actions
- [ ] Mobile menu
- [ ] Filters/search/forms when present

## Layout Checks

- [ ] No horizontal overflow
- [ ] No text clipping
- [ ] Text is readable and not mojibake
- [ ] No incoherent overlap
- [ ] Fixed controls do not resize unexpectedly

## Visual Usability Gate

- [ ] Brand/object immediately recognizable
- [ ] Primary hierarchy matches binding reference
- [ ] Key custom assets present, not generic placeholders
- [ ] First viewport composition matches reference
- [ ] Lower sections do not compete with hero unless the reference does so
- [ ] Page is acceptable as a first review build

## Asset Checks

- [ ] Images load
- [ ] Icons/ornaments load
- [ ] No unapproved hotlinks

## Visual Gaps

| Gap | Severity | Follow-up |
| --- | --- | --- |

## Exceptions Or Out-Of-Scope Routes

- Route:
- Reason:
- Risk:

## Signoff

- Production review:
- Deployment/PR:
- Remaining work:
- Final readiness claim follows weakest required route evidence status:

## Final Visual Pass Report

- URL:
- Binding reference:
- Latest screenshots:
- What changed:
- Runtime guards:
  - no full reference image:
  - real DOM links/text:
  - no overflow:
  - text encoding:
- Visual asset pipeline status:
- Resource atomicity status:
- First-viewport composition status:
- Mojibake/text encoding status:
- User feedback state:
- Verification:
- Known remaining visual gaps:
- Current status:
