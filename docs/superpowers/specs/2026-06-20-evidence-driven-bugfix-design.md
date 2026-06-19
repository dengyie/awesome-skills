# Evidence-Driven Bugfix Design

Date: 2026-06-20
Status: Proposed and user-approved for spec drafting
Target package: `evidence-driven-bugfix`

## Goal

Create a replacement-grade primary debugging and bugfix skill for `awesome-skills` that combines:

- root-cause-first debugging discipline
- failing-evidence-first implementation gating
- fresh verification before any success claim
- truthful completion behavior
- repeat-until-fixed looping, with narrow evidence-backed legal exits

This skill exists to stop a recurring failure mode:

- bugs are "fixed" before the root cause is understood
- code changes are made before stable failing evidence exists
- work is declared complete without fresh proof that the original bug is gone

## Problem Statement

The current combination of upstream skills is strong but fragmented:

- `systematic-debugging` is strong on root-cause investigation
- `test-driven-development` is strong on failing test discipline
- `verification-before-completion` is strong on completion honesty

The user wants a single primary bugfix workflow that bakes these constraints together by default instead of relying on the model to remember to compose multiple skills correctly.

The desired behavior is not merely "debug more carefully." The desired behavior is:

1. inspect logs and code first
2. obtain failing evidence before implementation
3. trace to root cause before fixing
4. apply only the minimal root-cause fix
5. re-run fresh verification against the same evidence chain
6. continue looping until fixed, unless a narrow evidence-backed legal exit applies
7. never imply success without fresh verification evidence

## Non-Goals

This skill should not:

- become a general software engineering skill
- act as a broad refactoring workflow
- replace a dedicated code review skill
- require scripts in v1 unless a script clearly removes ambiguity
- require a written artifact file for every small bugfix
- force automated tests in cases where they are not realistically available yet

## User Experience Intent

Tone target:

- collaborative
- direct
- disciplined
- evidence-oriented
- explicitly honest about uncertainty

The skill should feel like a strong debugging partner, not a scolding auditor. However, it must refuse to blur the distinction between:

- observation and hypothesis
- hypothesis and root cause
- code change and verified fix
- blocked and fixed

## Recommended Package Direction

Recommended package name:

- `evidence-driven-bugfix`

Reasoning:

- matches the repository's capability/workflow naming style
- foregrounds the central operating principle
- is broad enough for logs, code, reproduction, verification, and repair
- is less slogan-like than alternatives such as "truthful bugfix workflow"

## Role in the Repository

This package should be a first-class independent skill package in the same family as:

- `production-code-quality-review`
- `zero-to-website-design`
- `best-project-memory`
- `little-lighthouse-blog-publisher`

It is a replacement-grade primary bugfix workflow, not an add-on lint or optional post-check.

## Core Principles

The skill should encode these principles as non-negotiable workflow rules:

1. evidence before implementation
2. root cause before fix
3. fresh verification before success claim
4. truthful status over optimistic phrasing
5. repeat until fixed unless a proven legal exit applies

## Iron Laws

The skill should carry these three iron laws in `SKILL.md`:

```text
NO FIX WITHOUT FAILING EVIDENCE
NO ROOT-CAUSE GAP HIDDEN BY A SYMPTOM FIX
NO SUCCESS CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

## State Machine

The workflow is governed by the following states:

- `Investigating`
- `Reproduced`
- `Root-caused`
- `Fixing`
- `Verifying`
- `Fixed`
- `Manual-required`
- `Proven-external-blocker`

### State Meanings

`Investigating`

- logs, stack traces, changed files, data flow, and reproduction are still being gathered or clarified

`Reproduced`

- a stable failing evidence chain has been captured and can be reused later for verification

`Root-caused`

- a single root-cause hypothesis is supported by evidence strongly enough to justify a minimal fix

`Fixing`

- implementation of the minimal root-cause fix is in progress

`Verifying`

- the same failing evidence chain is being re-run fresh to determine whether the bug is actually fixed

`Fixed`

- only allowed when fresh verification evidence proves the original failure has been removed

`Manual-required`

- current progress is blocked by a required human action, permission, decision, credential, device, environment, or external access that the current session cannot produce

`Proven-external-blocker`

- evidence shows that the remaining blocker is outside the current code/control boundary and cannot be resolved in the current session

## Unified Loop Rule

The user explicitly wants this workflow to continue if the bug is not fixed.

Therefore the main rule is:

- failure to verify returns the workflow to investigation or root-cause analysis
- the workflow does not stop merely because a fix attempt was made
- the workflow continues until one of the following states is reached:
  - `Fixed`
  - `Manual-required`
  - `Proven-external-blocker`

This package must not allow optimistic, silent, or ambiguous early exits.

## The Six Gates

All bugfix work must pass through these six gates in order.

### Gate 1: Symptom Capture

Purpose:

- separate observed facts from guesses

Requirements:

- describe the symptom clearly
- capture the current visible failure mode
- identify the impact surface if known
- distinguish direct observation from user-reported information

Prohibited:

- proposing a fix before the symptom is clearly described
- presenting a guess as a fact

Pass condition:

- enough observed failure information exists to start reproduction or evidence gathering

### Gate 2: Failing Evidence Gate

Purpose:

- force a reusable failure signal before implementation

Accepted evidence, in priority order:

1. automated failing test
2. failing repro script
3. stable reproduction steps
4. deterministic failing log, error response, screenshot, or recording

Rules:

- no failing evidence means no repair claim and no "ready to fix" state
- investigation may continue without implementation
- implementation may not begin until a failing evidence chain exists

Pass condition:

- one clear failing evidence chain can later be re-run or re-checked to prove the fix

### Gate 3: Root Cause Investigation

Purpose:

- find the actual source of failure rather than patching symptoms

Requirements:

- read the relevant logs and error output carefully
- inspect stack traces and file/line context when available
- check recent code, config, and environment changes
- trace data flow and call flow backward where needed
- instrument component boundaries when evidence is incomplete

Rules:

- no symptom-only fix
- no parallel guess-fixes
- no "change it and see" workflow as the default strategy

Pass condition:

- a single root-cause hypothesis can be stated with supporting evidence

### Gate 4: Minimal Fix Plan

Purpose:

- constrain implementation scope so the outcome is attributable and testable

Requirements:

- identify the fix layer
- explain why that layer is the correct one
- define the smallest acceptable change
- record what is intentionally out of scope for this fix loop

Rules:

- one root-cause fix at a time
- no bundled cleanup
- no opportunistic refactor unless strictly required for the root-cause fix

Pass condition:

- the planned change maps directly to the established root cause

### Gate 5: Fresh Verification Gate

Purpose:

- prove that the original failure is gone using fresh evidence

Requirements:

- rerun or recheck the same evidence chain used at Gate 2
- confirm the original failure has turned green or disappeared as expected
- run the minimum necessary regression checks
- read the actual command or runtime output rather than inferring results

Rules:

- stale results do not count
- partial checks do not count as a fix claim
- confidence, visual inspection, or code plausibility do not count as verification

Pass condition:

- the original failure evidence now shows success and required regressions do not introduce a new blocker

### Gate 6: Truthful Completion Gate

Purpose:

- control reporting language and prevent false completion claims

Only three terminal outcomes are allowed:

1. `Fixed`
2. `Manual-required`
3. `Proven-external-blocker`

Rules:

- no "should be fixed"
- no "probably solved"
- no "looks good"
- no "done" without fresh evidence

If not fixed:

- report the actual state
- identify the blocker or next loop step
- do not imply completion

## Legal Exit Policy

The default behavior is to continue looping.

Only two non-fixed exits are allowed:

### `Manual-required`

Use only when evidence shows that progress now depends on something the current session cannot supply, such as:

- human approval or decision
- credentials, API keys, or secrets not available
- physical device or environment access
- account permissions
- external service setup owned by a human

### `Proven-external-blocker`

Use only when evidence shows that:

- the unresolved cause is outside the current code or execution boundary, and
- the current session cannot remove it

Neither exit may be described as "fixed."

## Workflow Behavior Expectations

When the skill is invoked, it should behave as a workflow driver, not a passive advice page.

Default expected behavior:

1. capture symptom
2. secure failing evidence
3. investigate to root cause
4. define the minimal fix
5. verify fresh against the original evidence
6. either:
   - declare `Fixed` with evidence
   - continue looping
   - declare a legal non-fixed exit with evidence

## Output Contract

The final user-facing output should be stable and structured.

Recommended sections:

- `Current state`
- `Symptom`
- `Failing evidence`
- `Root cause`
- `Fix applied`
- `Fresh verification`
- `Outcome`
- `If not fixed, next loop or blocker`

This output contract should be codified in `references/output-contract.md`.

## Package Structure

Recommended v1 package shape:

```text
evidence-driven-bugfix/
  SKILL.md
  agents/
    openai.yaml
  references/
    workflow-contract.md
    symptom-capture.md
    failing-evidence-gate.md
    root-cause-investigation.md
    minimal-fix-plan.md
    fresh-verification-gate.md
    truthful-completion.md
    manual-required-and-external-blockers.md
    output-contract.md
  tests/
    test_skill_package.py
```

## Why No Scripts in v1

Recommendation:

- do not include `scripts/` in v1

Reasoning:

- the first-order problem is workflow discipline, not missing automation
- references and package tests are enough to establish the contract
- scripts can be added later only when they reduce ambiguity or repeated manual effort

## Reference Responsibilities

### `references/workflow-contract.md`

- complete description of the six-gate workflow
- complete state machine
- unified loop rule
- legal exits

### `references/symptom-capture.md`

- how to distinguish direct evidence from inference
- minimum symptom record expectations

### `references/failing-evidence-gate.md`

- evidence hierarchy
- examples of acceptable and unacceptable failing evidence
- gate behavior when evidence is still insufficient

### `references/root-cause-investigation.md`

- log reading
- stack trace handling
- recent-change inspection
- backward tracing
- component-boundary instrumentation

### `references/minimal-fix-plan.md`

- writing a single root-cause fix hypothesis
- constraining scope
- anti-bundling rules

### `references/fresh-verification-gate.md`

- what qualifies as fresh verification
- re-running the same evidence chain
- minimum regression expectations

### `references/truthful-completion.md`

- allowed and forbidden completion language
- truthful status reporting rules

### `references/manual-required-and-external-blockers.md`

- distinction between hard blocker and weak excuse
- how to document a legal exit without implying success

### `references/output-contract.md`

- standard output sections
- how to report fixed vs not fixed outcomes

## Relationship to Upstream Skills

This package should inherit the best parts of three upstream skills:

- `systematic-debugging`
  - root-cause-first investigation
  - tracing and disciplined debugging loops

- `test-driven-development`
  - preference for a failing automated test
  - test-first mindset when feasible

- `verification-before-completion`
  - no completion claim without fresh evidence
  - anti-optimistic-reporting enforcement

The new package should not require the model to separately invoke those skills during normal use. Their essential constraints should be internalized into this skill's default workflow.

## Repository Integration

This package should be added to:

- root `README.md`
- `docs/usage/` as a user-facing guide
- `docs/usage/skill-matrix.md`
- repository package tests if needed

Formal release notes are not required for the initial design phase.

## Initial Package Tests

`tests/test_skill_package.py` should at minimum verify:

1. `SKILL.md` exists
2. all required reference files exist
3. `SKILL.md` contains the three iron laws
4. `SKILL.md` defines the legal terminal outcomes:
   - `Fixed`
   - `Manual-required`
   - `Proven-external-blocker`
5. `SKILL.md` clearly encodes:
   - no fix without failing evidence
   - no success claim without fresh verification evidence
   - retry/loop behavior until fixed or legally blocked

## Risks

### Risk: Skill becomes too heavy for small bugs

Mitigation:

- keep references crisp
- allow lightweight evidence forms when automated tests are not feasible yet
- keep artifact files optional in v1

### Risk: Skill still permits vague completion language

Mitigation:

- isolate truthful completion into its own explicit gate
- codify prohibited phrasing in `truthful-completion.md`

### Risk: Infinite unproductive looping

Mitigation:

- allow only narrow, evidence-backed legal exits
- require explicit blocker reporting
- forbid silent abandonment or false success

### Risk: Overlap with review skill causes confusion

Mitigation:

- clearly position this package as a bugfix execution workflow, not a review workflow

## Recommended Next Step

Implement the first package version using the structure above, then add:

1. package contract tests
2. README and usage guide integration
3. optional future scripts only if real repeated pain appears

## Approval Snapshot

Confirmed during brainstorming:

- package name: `evidence-driven-bugfix`
- role: replacement-grade primary bugfix skill
- tone: collaborative but cannot lie
- test gate: failing evidence is mandatory; automated test is preferred, not the only acceptable gate
- loop rule: continue until fixed unless a legal evidence-backed blocker applies
- legal exits: `Fixed`, `Manual-required`, `Proven-external-blocker`
