# V25 Zero-To-Website Interactive Reference Implementation Plan

## Milestone

Prevent `zero-to-website-design` from satisfying a binding design image by placing the full screenshot on the page and adding transparent hotspots.

## Problem

The V20-V24 fidelity rules require selected images, itemized audits, and verifiable evidence. A new failure mode remains: an agent may treat a binding reference as the shipped page image. That can look visually identical, but it is not a real website implementation because text, controls, sections, links, charts, and responsive behavior are not implemented as maintainable, accessible, interactive UI.

## Scope

P0/P1:

- Add a regression test for the full-page screenshot plus transparent hotspot anti-pattern.
- Update the main skill workflow to require binding references to be rebuilt as real DOM, components, local assets, and interactions.
- Update fidelity, QA, route acceptance, QA template, and usage docs to classify screenshot-as-page implementations as blocking.
- Record the project-memory decision and active work state.

Out of scope:

- Automated DOM-versus-image structural analysis.
- Subagent pressure testing.
- New generated visual assets.

## Acceptance

- Tests assert that screenshot-as-page is forbidden and that interactive component implementation is required.
- `Visual Delivery Ready` is blocked when a route uses a full-page reference screenshot as the primary implementation surface.
- Screenshots remain allowed as reference evidence, QA artifacts, and limited non-interactive decorative or raster asset inputs.
