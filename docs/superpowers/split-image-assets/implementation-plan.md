# Split Image Assets Unified Implementation Plan

Date: 2026-06-30
Status: Canonical implementation plan for the current `split-image-assets` installer UX line
Design source: `docs/superpowers/split-image-assets/design.md`

## Authority

This is the single implementation plan for the current `split-image-assets` installer UX redesign.

It replaces the prior canonical milestone that focused on contract unification and maintainability hardening as the active execution plan for this package line.

All future development on this line should execute from this plan unless a newer canonical plan explicitly replaces it.

## Execution Contract

```text
Milestone：split-image-assets isolated installer UX V1
目标：让用户优先通过隔离环境获得 recommended 级安装体验，并让 installer、runtime preflight、docs、tests 使用同一套 capability 语言
P0/P1 范围：
- P0：建立 container-first、docker-compatible 的默认安装路径
- P0：统一 doctor / install / verify / runtime preflight 的 capability model
- P0：默认推荐必须清楚落到 recommended，而不是 host-global 环境污染
- P1：提供 venv fallback
- P1：支持 mac-apple-silicon 主路径与 linux-cuda 次路径
- P1：补 explain surface、docs、tests 和 runtime wording 闭环
不做的 P2/P3：
- 模型权重全自动下载编排
- GUI installer
- Windows 首发支持
- 完整升级 / 卸载 / 迁移系统
- 所有第三方 provider 的精细自动编排
- 脱离本 skill 的通用安装器产品化
Manual-required：
- 用户机器上的真实容器运行时安装与授权
- 任何真实外部容器镜像拉取限制
- 任何需要人工确认的系统级依赖安装
阶段上限：3
阶段拆分：
- 阶段 1：Shared capability model and doctor/verify surface
- 阶段 2：Container-first install path
- 阶段 3：Runtime integration, docs, and tests
验收标准：
- 用户可以先运行 doctor 得到清晰推荐
- 默认 mode 为 container，默认 preset 为 recommended
- 容器可用时不默认污染用户 host Python
- install 后 verify 能给出清晰 tier 与 next step
- runtime preflight 能引用同一套 installer capability 语言
- docs 与脚本 contract 一致，关键测试通过
停止条件：
- 当前 milestone 的 P0/P1 完成并通过必要验证
- 阶段数量达到上限
- 同一 P0/P1 阻断连续 3 次修复后仍无法通过
- 关键外部依赖缺失导致当前环境无法完成本 milestone 验收
```

## Current Diagnosis

This milestone is driven by five concrete issues:

1. `check_extraction_environment.py` detects missing capability, but it is not a coherent installer experience
2. the package lacks a clear product surface for setup: users cannot reliably answer “what should I run next”
3. the default recommendation does not yet protect users from host-environment pollution strongly enough
4. docs, runtime preflight, and future installer commands would currently drift unless they share one capability model
5. the package has no canonical container-first path even though isolation is now a user-confirmed requirement

## Phase Strategy

This plan treats installer UX, runtime language, docs, and tests as one bounded delivery loop. The milestone should not fragment into “just docs” or “just scripts.”

### Phase 1: Shared Capability Model And Doctor/Verify Surface

**Phase goal:** establish one environment truth model and expose it through clean read-only user surfaces.

**Corresponding P0/P1:**

- P0 shared capability language
- P0 recommendation clarity
- P1 profile and preset resolution

**Expected deliverables:**

- a shared package-local capability model or probe library
- profile detection for `mac-apple-silicon` and `linux-cuda`
- runtime mode detection for Docker-compatible container paths and `venv`
- clear tier mapping for `draft`, `recommended`, and `production`
- a `doctor` entrypoint with action-first output
- a `verify` entrypoint with post-install readiness output

**Required behavior:**

- `doctor` does not mutate the environment
- `verify` distinguishes `installed`, `runtime_ready`, and `production_ready`
- output leads with conclusion, current tier, and recommended next command
- Python mismatch is surfaced before a long dependency list

**Verification:**

- focused tests for profile detection
- focused tests for mode routing
- focused tests for tier classification
- command output contract tests for `doctor` and `verify`

### Phase 2: Container-First Install Path

**Phase goal:** make isolated setup the default success path.

**Corresponding P0/P1:**

- P0 container-first default
- P0 Docker-compatible routing
- P1 venv fallback

**Expected deliverables:**

- an `install` entrypoint
- Docker-compatible runtime detection and routing for:
  - `docker`
  - `podman`
  - `colima`-compatible Docker CLI path
- default resolution to `container + recommended`
- explicit `venv` fallback when container runtime is unavailable or declined
- isolated environment conventions for:
  - working directory mounts
  - output directory mounts
  - cache/model directory mounts
  - wrapper or launch conventions

**Required behavior:**

- `install` must not default to host-global Python mutation
- container mode should be chosen automatically when available
- fallback to `venv` should be explicit and honest
- install stages should record `installed`, `skipped`, `failed`, and `manual_step_required`
- `install` should trigger `verify` automatically after setup work

**Verification:**

- container availability routing tests
- default resolution tests
- fallback routing tests
- stage result contract tests

### Phase 3: Runtime Integration, Docs, And Tests

**Phase goal:** make runtime preflight, package docs, and tests converge on the installer UX.

**Corresponding P0/P1:**

- P0 runtime and installer language unification
- P1 docs and test closure
- P1 explain surface

**Expected deliverables:**

- an `explain` entrypoint for preset, profile, component, and why-not-production guidance
- runtime preflight wording aligned to the new installer surfaces
- `split-image-assets/SKILL.md` aligned to the new install path
- `split-image-assets/references/workflow.md` aligned to the new install path
- `split-image-assets/references/pipeline-recipes.md` aligned to the new install path
- `docs/usage/split-image-assets.md` aligned enough to present the new onboarding path honestly
- regression tests that cover command contracts and docs alignment

**Required behavior:**

- runtime preflight should recommend `doctor`, `install`, or `verify` rather than only dumping missing tools
- docs must describe `container` as the default mode
- docs must describe `recommended` as the default preset
- `explain` must answer why `recommended` is default and why a system is not `production`

**Verification:**

- command output contract tests for `explain`
- docs sync tests
- runtime wording tests
- final package review against milestone diff

## Detailed Task List

## Phase 1 Tasks

- [ ] Extract or introduce a shared capability model beneath current environment detection.
- [ ] Define canonical profile, mode, preset, and readiness fields.
- [ ] Refactor `check_extraction_environment.py` to consume shared capability logic or clearly hand off to it.
- [ ] Add `doctor` with action-first output.
- [ ] Add `verify` with post-install readiness output.
- [ ] Add tests for tier mapping, profile detection, and output contract behavior.

## Phase 2 Tasks

- [ ] Add an `install` entrypoint that defaults to `container + recommended`.
- [ ] Add Docker-compatible runtime routing for `docker`, `podman`, and compatible `colima` paths.
- [ ] Define isolated mount, cache, and wrapper conventions.
- [ ] Add explicit `venv` fallback routing without making it the default experience.
- [ ] Add stage-result reporting and automatic verify handoff.
- [ ] Add tests for routing, fallback, and stage-result contracts.

## Phase 3 Tasks

- [ ] Add `explain` for preset, profile, component, and why-not-production guidance.
- [ ] Update runtime preflight wording to route users into installer UX.
- [ ] Update package-facing docs to reflect container-first onboarding.
- [ ] Add docs and command contract tests.
- [ ] Run production-code-quality-review on the milestone diff.
- [ ] Fix any remaining P0/P1 blockers before closure.

## File Ownership Map

### Canonical policy docs

- `docs/superpowers/split-image-assets/design.md`
- `docs/superpowers/split-image-assets/implementation-plan.md`

These define the installer UX authority and milestone order.

### Skill and package docs

- `split-image-assets/SKILL.md`
- `split-image-assets/references/workflow.md`
- `split-image-assets/references/pipeline-recipes.md`
- `split-image-assets/references/confirmation-prompts.md`
- `split-image-assets/references/asset-package-contract.md`
- `docs/usage/split-image-assets.md`

These must reflect the canonical docs and must not drift into a separate installation story.

### Code ownership hotspots

- `split-image-assets/scripts/check_extraction_environment.py`
- new shared capability helpers
- new installer UX entrypoints:
  - `doctor`
  - `install`
  - `verify`
  - `explain`
- supporting runtime-mode and routing helpers

### Test ownership hotspots

- `split-image-assets/tests/test_skill_package.py`
- any extracted installer-focused test modules created during this milestone

## Verification Order

Use this order unless a narrower faster check is clearly sufficient for the current phase:

1. targeted unit or contract tests for the changed installer surface
2. broader `split-image-assets` regression
3. production-code-quality-review on the milestone diff

Do not claim closure from docs alone when command output, preflight wording, or routing behavior still disagree.

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

- automated model weight acquisition and caching orchestration
- Windows profile support
- full upgrade / uninstall / migration lifecycle
- richer container image publishing strategy
- repo-wide shared installer abstractions for other skills
- GUI onboarding

## Done Definition

This milestone is done only when:

1. installer UX has a canonical container-first design
2. `doctor`, `install`, `verify`, and runtime preflight share one capability language
3. `recommended` is the default recommendation
4. container mode is the default path when available
5. `venv` exists as a bounded fallback
6. package docs reflect the new onboarding model
7. tests verify command and doc contract behavior
8. the milestone review has no remaining P0/P1 blockers
