# V26 Zero-To-Website Design Rounds Plan

## Research Notes

- OpenAI Codex Skills guidance treats `SKILL.md` as task instructions that should be clear about when to use a skill and what outputs it should produce. For this package, the main task is end-to-end website delivery, so the main skill should expose the round contract early instead of burying it in later QA language.
- Agent skill authoring guidance emphasizes progressive disclosure: keep the main skill as a compact router and move detailed process rules to references. The round-by-round design method is large enough to deserve `references/design-rounds.md`.
- The local `skill-creator` guidance says skill updates should come from concrete failure modes and should close rationalizations. The current failure mode is that agents treat the 13 gates as a checklist they can complete in one pass, skip user visual selection, start coding before design artifacts, or collapse visual QA into an end-of-task afterthought.

Sources checked:

- OpenAI Codex Skills: https://developers.openai.com/codex/skills
- Agent Skills specification: https://agentskills.io/specification
- Anthropic Agent Skills best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Anthropic Agent Skills engineering note: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

## Milestone

Make `zero-to-website-design` enforce explicit website design rounds before final delivery.

## P0/P1 Scope

- Add a `design-rounds.md` reference that defines required rounds, outputs, entry criteria, exit criteria, user confirmation points, and no-skip rules.
- Update `SKILL.md` to read the round contract early and block broad implementation before required round outputs exist.
- Update implementation and QA templates so downstream projects record round state.
- Update usage docs so users understand the staged design process.
- Add regression tests for the round contract.

## Out Of Scope

- New code-generation scripts.
- Subagent pressure testing in this pass.
- Full visual QA automation.

## Acceptance

- Tests fail before the new round contract exists and pass after it is implemented.
- The skill distinguishes rounds from milestone phases: rounds are design workflow gates inside a milestone; phases remain delivery/review units.
- No `Visual Delivery Ready` claim is allowed when required rounds are skipped, unrecorded, or collapsed into a single final checklist.
