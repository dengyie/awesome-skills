# Zero-To-Website Design V14 Workflow Doc Alignment Plan

> Status: Planned
> Target surface: `zero-to-website-design` public usage docs and regression tests
> Phase type: documentation contract hardening

## Goal

Align the public `docs/usage/zero-to-website-design.md` workflow summary with the actual 12-step workflow in `zero-to-website-design/SKILL.md`.

## Why This Phase

The skill body now includes 12 required workflow steps, ending with project-memory integration for long-running website work. The public usage guide still says the workflow has "eleven gates" and stops its numbered list at "Harden and deliver." That mismatch can mislead users and weakens the package's documented project-memory behavior.

## Scope

In scope:

- update the public usage guide to describe 12 gates
- include project-memory integration as the twelfth workflow step
- add regression coverage so `SKILL.md` and the usage guide cannot drift on this visible workflow count again
- update project memory for this phase

Out of scope:

- changing the actual `SKILL.md` workflow
- adding new templates or references
- changing website-generation behavior

## Acceptance Criteria

- usage docs say the workflow has 12 gates
- usage docs include project-memory integration in the numbered workflow summary
- tests protect the visible 12-step usage summary
- `zero-to-website-design` package tests pass
- skill validation passes
- production review reports no confirmed blocking issue

## Decision Record

- Decision: Treat usage-doc workflow drift as V14 instead of opening a new feature-heavy hardening phase.
- Rationale: After V11-V12, the package contract is already strong; the clearest immediate defect is a public documentation mismatch that can confuse users about memory integration.
- Risk: This phase is small and documentation-focused.
- Mitigation: Keep the scope narrow and add a direct regression test.

## Suggested Commit Shape

- `docs(阶段24): align zero-to-website workflow docs`
