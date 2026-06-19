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

| Route | Reference Screenshot | Implementation Screenshot | Side-by-side comparison | Fidelity Status | Blocking visual deviations | Accepted visual gaps | Next fix |
| --- | --- | --- | --- | --- | --- | --- | --- |

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
- [ ] No incoherent overlap
- [ ] Fixed controls do not resize unexpectedly

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
