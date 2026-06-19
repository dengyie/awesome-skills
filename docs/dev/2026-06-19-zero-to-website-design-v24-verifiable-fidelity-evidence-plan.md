# Zero-To-Website Design V24 Verifiable Fidelity Evidence Plan

## Problem

The V23 itemized audit requires route/page items to be compared, but an agent can still fill the audit with subjective statements that are hard to verify later. The next failure mode is "audit theater": rows exist, but they do not point to concrete screenshot regions, crops, annotations, or post-fix evidence.

## Goal

Require every binding-route audit row to include verifiable visual evidence and require changed rows to be re-evidenced after fixes.

## Scope

- Strengthen `design-fidelity-loop.md` with evidence quality rules.
- Update QA template columns so each item has reference and implementation regions plus evidence quality.
- Update usage docs and tests.
- Sync the local installed skill after validation.

## Out Of Scope

- Building an automated image diff tool.
- Mandating a single annotation format.
- Applying the workflow to an external website project.

## Acceptance

- Tests protect the verifiable evidence requirements.
- Skill validation passes.
- Local installed `zero-to-website-design` matches the repository package.
