# Zero-To-Website Design V23 Page Item Fidelity Audit Plan

## Problem

The current fidelity loop requires side-by-side screenshots and difference summaries, but it still lets an agent summarize visual drift too broadly. Real usage showed that pages can remain far from the selected design because the agent does not compare every page section, component silhouette, asset slot, typography block, spacing relationship, and responsive state item by item.

## Goal

Make page-by-page, item-by-item design comparison a required evidence gate before claiming visual delivery or design match.

## Scope

- Add a page item fidelity audit contract to the main skill workflow.
- Expand `design-fidelity-loop.md` with a required per-page audit table and failure rules.
- Expand QA and route acceptance expectations so every binding route must include itemized comparison rows.
- Update QA report template and usage docs.
- Add regression coverage for the new contract.

## Out Of Scope

- Automated pixel-diff implementation.
- Real project page refactoring.
- New generated example images.

## Acceptance

- Tests fail if page/item fidelity audit language disappears.
- Skill validation passes.
- Local installed `zero-to-website-design` is synced after repository changes.
