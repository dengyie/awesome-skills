# Zero-To-Website Design V20 Design Fidelity Loop Plan

## Milestone

Make `zero-to-website-design` produce pages that stay close to binding design images instead of stopping at broad structural similarity.

## Problem

The current workflow has provenance, implementation mapping, and browser QA, but it does not force a sufficiently concrete design-reference fidelity loop:

- binding screenshots are not always decomposed into measurable layout, typography, color, asset, and responsive facts
- generated UI imagery or component prompt work is optional and underspecified
- implementation screenshots can be checked only for general QA, not direct side-by-side fit against the source image
- final delivery can report visual gaps without proving that blocking deviations were fixed or consciously downgraded

## P0/P1 Scope

- Add a dedicated `design-fidelity-loop.md` reference.
- Require reference decomposition before implementation when a binding design image exists.
- Require UI asset/component prompt planning when existing assets cannot reproduce a reference.
- Require implementation screenshots, side-by-side comparison, deviation logs, and fix loops before `Visual Delivery Ready`.
- Update templates and usage docs so real projects can carry the fidelity evidence.
- Add regression tests for the new contract.

## Out Of Scope

- Building an image-diff engine.
- Mandating pixel-perfect equality for every project.
- Replacing human judgment where a design image is ambiguous.
- Updating unrelated skills.

## Design

The new loop sits between source authority and implementation QA:

1. Decompose each binding reference into measurable facts.
2. Set a route-specific fidelity budget: which deviations block delivery and which are accepted gaps.
3. Plan missing visual assets, including image-generation prompts for UI illustrations, panels, textures, icons, or component-like art when needed.
4. Implement route sections against the decomposition.
5. Capture implementation screenshots at the same viewport as the reference.
6. Produce side-by-side comparison evidence and a difference summary.
7. Fix blocking deviations and repeat screenshots until the route can honestly claim its readiness state.

## Acceptance

This pass is complete when tests prove the skill, usage guide, reference docs, and templates all require the loop and validation passes.
