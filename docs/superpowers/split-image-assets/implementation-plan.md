# Split Image Assets Unified Implementation Plan

Date: 2026-06-29
Status: Canonical implementation plan for the current `split-image-assets` refactor line
Design source: `docs/superpowers/split-image-assets/design.md`

## Authority

This is the single implementation plan for the current `split-image-assets` redesign.

It supersedes all earlier split-image-assets plans that previously lived under dated `docs/superpowers/plans/` paths.

All future development on this line should execute from this plan unless a newer canonical plan explicitly replaces it.

## Execution Contract

```text
Milestone：split-image-assets agent-first contract unification and maintainability hardening
目标：把 split-image-assets 统一到一套可执行的 stop/continue contract、editability-first asset routing contract、以及更稳定的 package-local architecture 上
P0/P1 范围：
- P0：消除 canonical docs、skill refs、writer defaults、validator rules、tests 之间的 contract 漂移
- P1：建立 shared contract source，拆分 validator / review writer 的高耦合职责，补足精确 contract tests
不做的 P2/P3：
- 新增上游模型集成
- OCR / 字体识别 / 更强语义理解
- 仓库级通用交互框架抽象
- 与当前 milestone 无关的全仓大重构
Manual-required：
- 任何真实人工审批、真实外部工具安装、真实上游专业输出
阶段上限：3
阶段拆分：
- 阶段 1：Canonical contract extraction
- 阶段 2：Writer / validator architecture refactor
- 阶段 3：Test and drift-proof hardening
验收标准：
- 单一 canonical 设计文档和实现计划生效
- stop taxonomy、asset routing、formal-state rules 在 docs / code / tests 中一致
- approximate_reconstruction 按 user-decision 统一
- 共享 contract source 取代关键重复定义
- 当前 split-image-assets 回归通过
停止条件：
- 当前 milestone 的 P0/P1 完成并通过必要验证
- 阶段数量达到上限
- 同一 P0/P1 阻断连续 3 次修复后仍无法通过
- 关键外部依赖缺失导致当前环境无法完成本 milestone 验收
```

## Current Diagnosis

Based on the current codebase state, this plan is driven by four concrete issues:

1. the canonical interaction and routing intent has been spread across multiple overlapping specs and plans
2. `record_quality_review.py` and `validate_asset_package.py` both own contract data and are vulnerable to drift
3. `approximate_reconstruction` currently has a known contract mismatch risk between docs and code defaults
4. `test_skill_package.py` is too concentrated to remain the only sustainable regression surface

## Phase Strategy

This plan does not treat docs, code, and tests as separate initiatives. Each phase must close a user-visible or release-gating loop.

### Phase 1: Canonical Contract Extraction

**Phase goal:** make one contract authoritative and eliminate ambiguity about how the package should behave.

**Corresponding P0/P1:**

- P0 canonical doc authority
- P0 exact gate taxonomy alignment
- P1 asset value routing authority

**Expected deliverables:**

- `split-image-assets/SKILL.md` aligned to the canonical design
- `split-image-assets/references/workflow.md` aligned to the canonical gate taxonomy
- `split-image-assets/references/confirmation-prompts.md` aligned to the canonical stop contract
- `split-image-assets/references/asset-package-contract.md` aligned to the canonical formal-state and routing contract
- `docs/usage/split-image-assets.md` aligned enough to avoid user-facing contradiction
- tests that assert exact key mappings and exact gate semantics where drift previously occurred

**Key contract moves:**

- preserve exactly three stop classes
- treat medium/high-risk semantic divergence as a trigger for `user-decision`, not a fourth class
- keep progress reporting in commentary only
- make `approximate_reconstruction` consistently `user-decision`
- document placeholder/object-record behavior for `rebuild_downstream`

**Verification:**

- targeted doc and contract tests
- exact mapping tests for gate defaults and confirmation surfaces

### Phase 2: Writer / Validator Architecture Refactor

**Phase goal:** reduce contract drift by moving from duplicated policy ownership to package-local shared ownership.

**Corresponding P0/P1:**

- P0 drift prevention between writer and validator
- P1 maintainability hardening for future routing/gate work

**Expected deliverables:**

- a shared package-local contract module for enums, gate mappings, confirmation keys, pause defaults, and related taxonomy
- `record_quality_review.py` refactored to consume the shared contract source
- `validate_asset_package.py` refactored to consume the shared contract source
- writer responsibilities separated enough that CLI parsing, metadata mutation, and report append logic are no longer tangled in one path
- validator responsibilities separated enough that metadata, object routing, preview/filesystem, and candidate-evidence checks are no longer one undifferentiated mass

**Required behavior changes:**

- remove repeated hard-coded gate/category definitions where possible
- ensure no writer-emitted default can contradict validator expectations
- make the `approximate_reconstruction` default category impossible to drift silently

**Verification:**

- focused unit tests for the shared contract source
- targeted writer and validator tests covering both happy and rejection paths
- full split-image-assets regression before phase close

### Phase 3: Test And Drift-Proof Hardening

**Phase goal:** make future contract regressions obvious and cheaper to review.

**Corresponding P0/P1:**

- P1 sustainable regression surface
- P1 code review and maintenance hardening

**Expected deliverables:**

- split or reorganized test structure with domain ownership, either by module extraction or by clearly partitioned sections if full file split is too risky for the same milestone
- exact contract tests for:
  - stop-class mapping
  - confirmation key defaults
  - `approximate_reconstruction` semantics
  - asset value routing legality
  - formal-state vs commentary separation
- production-code-quality-review pass on the milestone diff

**Verification:**

- full `split-image-assets` test suite
- code review pass with no remaining P0/P1 blockers

## Detailed Task List

## Phase 1 Tasks

- [ ] Align `split-image-assets/SKILL.md` with the canonical design doc instead of allowing it to freehand duplicate policy.
- [ ] Align `split-image-assets/references/workflow.md` to the normalized gate taxonomy and continue-versus-stop rules.
- [ ] Align `split-image-assets/references/confirmation-prompts.md` to the exact allowed stop classes and grill-me-shaped stop contract.
- [ ] Align `split-image-assets/references/asset-package-contract.md` to the formal-state-only rule and the editability-first routing model.
- [ ] Add or tighten tests that assert exact mapping behavior, not just general wording presence.
- [ ] Fix any doc/code/test mismatch uncovered by those exact tests before moving on.

## Phase 2 Tasks

- [ ] Extract shared enums, gate mappings, confirmation defaults, and related contract constants into a package-local shared module.
- [ ] Update `record_quality_review.py` to import shared contract definitions and route metadata mutations through narrower helpers.
- [ ] Update `validate_asset_package.py` to import the shared contract definitions and split validation responsibilities by domain.
- [ ] Add targeted tests for the shared contract module and for the writer/validator integration points.
- [ ] Verify that current behavior still supports the intended package contract and stop/continue model.

## Phase 3 Tasks

- [ ] Reduce test concentration by separating high-risk contract tests from large scenario tests.
- [ ] Add exact regression coverage for the known historical drift points.
- [ ] Run the production review loop against the final milestone diff.
- [ ] Close only after P0/P1 review blockers are fixed or explicitly proven nonexistent.

## File Ownership Map

### Canonical policy docs

- `docs/superpowers/split-image-assets/design.md`
- `docs/superpowers/split-image-assets/implementation-plan.md`

These are the governing docs. They define intent and execution order.

### Skill and package docs

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `docs/usage/split-image-assets.md`

These must reflect the canonical docs. They are not allowed to invent divergent policy.

### Code ownership hotspots

- `split-image-assets/scripts/init_asset_package.py`
- `split-image-assets/scripts/record_quality_review.py`
- `split-image-assets/scripts/validate_asset_package.py`
- any new shared package-local contract or helper modules

### Test ownership hotspots

- `split-image-assets/tests/test_skill_package.py`
- any extracted package test modules created during Phase 3

## Verification Order

Use this order unless a narrower faster check is clearly sufficient for the current phase:

1. targeted unit or contract tests for the changed surface
2. broader split-image-assets regression
3. production-code-quality-review on the milestone diff

Do not claim closure from doc wording alone when code defaults or validators still disagree.

## Review Gate

Each phase must end with a production-code-quality-review pass using the local `production-code-quality-review` skill.

The report must call out:

- severe issues
- medium issues
- non-blocking suggestions
- security risk
- stability risk
- maintainability risk
- test coverage
- quality score
- pass status

P0/P1 blockers must be fixed in the same phase before proceeding.

## Backlog

These are valid future items but are not part of the current milestone unless they become direct P0/P1 blockers:

- deeper package modularization beyond contract hotspots
- broader repo-wide documentation cleanup
- richer downstream reconstruction helpers
- stronger fixture-generation utilities
- generalized shared interaction abstractions for other skills

## Done Definition

This milestone is done only when:

1. the canonical docs are the clear authority
2. the package-facing docs match them
3. code defaults and validators match them
4. tests verify exact contract behavior
5. the milestone review has no remaining P0/P1 blockers
