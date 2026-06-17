# best-project-memory V2 开发文档

## 1. 文档目的

本文档定义 `best-project-memory` 的 V2 开发方案。

V1 已经把该 skill 从轻量规则说明升级为正式 skill 包，具备：

- `SKILL.md` 入口
- `references/` 参考层
- `scripts/` helper 层
- `tests/` 回归保护层

但 V1 仍主要是“repo-native continuity workflow + helper scripts”的组合。V2 的目标不是简单继续加文档和脚本，而是把它升级成一个真正可治理的项目连续性中枢。

## 2. V2 定位

### 2.1 核心定位

V2 定位为：

> 一个面向仓库内项目连续性、状态治理、证据绑定、多 skill 协同和大项目扩展的 repo-native memory governance layer。

### 2.2 它要解决的问题

V2 要解决的不是“项目里没有记忆文件”，而是以下更深一层的问题：

1. 记忆文件是否持续保持高质量
2. 当前状态是否可信、可压缩、可追踪
3. 决策和行动是否能绑定到代码与验证证据
4. 不同 skill 是否能在统一 memory contract 上协作
5. 项目规模变大后 memory 是否会失控膨胀

## 3. V2 设计原则

### 3.1 轻量优先

继续以 Markdown + 仓库内文件为主，不引入数据库或外部状态服务。

### 3.2 治理优先

V2 不是“增加更多存储位置”，而是增加治理机制，让 memory 质量稳定。

### 3.3 证据优先

能自动提取的工程证据尽量自动提取，例如：

- 当前分支
- 变更文件
- 最近验证命令
- workstream 关联文件

### 3.4 分层优先

将 memory 分为：

- 当前态
- 过程态
- 提升态
- 压缩态

避免所有信息堆到一个长文档里。

### 3.5 渐进增强

仓库可以从 core files 起步，再逐步引入 workstreams、snapshots、lint、compaction，不要求一次到位。

## 4. V2 目标

V2 目标覆盖四个方向。

### 4.1 自动治理

减少手工维护带来的遗漏、漂移和失真。

### 4.2 证据绑定

把 memory 和 branch、changed files、tests、验证状态建立更稳定的关联。

### 4.3 多 skill 协同

让其他 skill 能基于统一 contract 读写 memory，而不是各写各的。

### 4.4 大项目扩展

支持：

- 多阶段
- 多 workstream
- 长周期迭代
- 会话交接

## 5. 非目标

V2 不做以下事情：

- 不替代 git 历史
- 不替代 issue tracker
- 不替代聊天记录
- 不做全自动项目管理系统
- 不在没有足够证据时自动推断高语义结论

## 6. 核心架构

V2 采用三层架构：

### 6.1 Memory Surface

仓库内 `.codex-memory/` 作为统一存储面。

### 6.2 Governance Engine

通过脚本执行：

- 初始化
- 同步
- 提升
- 压缩
- lint

### 6.3 Memory Contract

通过 `SKILL.md + references/*.md` 定义：

- 哪些文件的职责是什么
- 什么事件触发什么更新
- 什么叫高质量 memory
- 其他 skill 应怎样接入

## 7. V2 目录结构

### 7.1 仓库内 memory 目录

建议结构：

```text
.codex-memory/
  project-state.md
  todo.md
  decisions.md
  session-log.md
  handoffs/
  phases/
  workstreams/
  snapshots/
```

### 7.2 各对象职责

#### `project-state.md`

全局当前真相。

特点：

- 只存当前摘要
- 不存长历史
- 项目级别，不承接每条子任务细节

#### `todo.md`

全局动作清单。

特点：

- 保持短
- 保持可执行
- 优先放项目级下一步或各 workstream 的最高优先项

#### `decisions.md`

稳定决策层。

特点：

- ADR-lite
- 记录 rationale、impact、rollback trigger

#### `session-log.md`

过程历史层。

特点：

- append-heavy
- 允许长，但必须可 compact

#### `handoffs/`

会话交接层。

特点：

- 面向继续工作
- 强调 exact next actions

#### `phases/`

阶段总结层。

特点：

- 面向 milestone
- 不是逐步日志，而是压缩后的阶段知识

#### `workstreams/`

V2 新增。

特点：

- 面向并行子任务
- 限定边界
- 支撑大项目

示例：

- `auth-refactor.md`
- `release-hardening.md`
- `docs-refresh.md`

#### `snapshots/`

V2 新增。

特点：

- 机器生成优先
- 存证据型快照
- 不承担高语义总结职责

## 8. 状态模型

V2 使用轻量信息升级模型。

### 8.1 Ephemeral

临时上下文，尚不进入 memory。

### 8.2 Active

已影响当前工作，进入：

- `project-state.md`
- `todo.md`
- `workstreams/*.md`

### 8.3 Recorded

已发生且值得保留，进入：

- `session-log.md`

### 8.4 Promoted

被证明对未来持续有价值，进入：

- `decisions.md`
- `phases/*.md`
- `handoffs/*.md`

### 8.5 Compacted

细节不再保留在主视图中，被压缩为：

- 阶段总结
- handoff 摘要
- compacted session summary

## 9. 全局状态与 workstream 分层

V2 明确以下边界：

- `project-state.md` 只保留全局摘要
- `workstreams/*.md` 承担并行任务的具体状态
- `todo.md` 只保留关键可执行动作

目标是避免全局面板再次退化成长文档。

## 10. V2 脚本体系

V2 脚本分四类。

### 10.1 初始化类

保留并扩展：

- `init_memory.py`

V2 目标能力：

- 初始化 core files
- 初始化 `handoffs/`
- 初始化 `phases/`
- 初始化 `workstreams/`
- 初始化 `snapshots/`
- 支持 repair 缺失结构

### 10.2 同步类

新增：

- `snapshot_state.py`
- `sync_workstream.py`

#### `snapshot_state.py`

职责：

- 读取 branch
- 读取 changed files
- 读取验证命令或验证结果
- 输出 snapshot
- 可选回写 `project-state.md` 摘要字段

#### `sync_workstream.py`

职责：

- 更新 `workstreams/<slug>.md`
- 同步 focus、blockers、files、next actions、validation status

### 10.3 提升 / 压缩类

新增：

- `promote_decision.py`
- `compact_session.py`
- `generate_handoff.py`

#### `promote_decision.py`

职责：

- 从 session 或 workstream 中提取高价值决策
- 强制补足决策字段

#### `compact_session.py`

职责：

- 压缩过长 `session-log.md`
- 保留阶段摘要
- 降低噪音堆积

#### `generate_handoff.py`

职责：

- 从当前 memory 生成交接包
- 尽量自动带上 project-state / todo / workstream / snapshot 关键信息

### 10.4 检查类

新增：

- `stale_todo_check.py`
- `memory_lint.py`

#### `stale_todo_check.py`

职责：

- 检测长期未动的 TODO
- 帮助发现失效项和脏状态

#### `memory_lint.py`

职责：

- 检查 required sections
- 检查 project-state 与 workstream 是否冲突
- 检查 handoff 是否缺少 next actions
- 检查 decisions 是否缺少 rationale

## 11. 自动化策略

V2 不建议默认全自动写所有语义字段，而采用三档模式。

### 11.1 Suggest 模式

- 只给建议
- 不改文件

### 11.2 Apply 模式

- 只改可预测位置
- 适合 append、snapshot、handoff 生成

### 11.3 Enforce 模式

- 用于 lint / CI / release gate
- 不直接修复，发现问题就失败

## 12. Memory Contract

V2 contract 分三层。

### 12.1 Surface Contract

定义：

- 标准目录结构
- 每个对象的职责
- 哪些文件允许脚本主导写入
- 哪些文件以人工语义为主

建议新增：

- `references/surface-contract.md`

### 12.2 Update Contract

定义：

- 什么事件触发什么 memory 更新

建议新增：

- `references/update-triggers.md`

示例事件：

- 开始 repo 工作
- 完成一轮重要改动
- 做出 durable decision
- 出现并行 workstream
- 会话暂停
- 日志过长

### 12.3 Quality Contract

定义：

- 什么叫高质量 memory
- 常见坏味道
- 修复策略

建议新增：

- `references/quality-rules.md`

## 13. 多 skill 接入模型

V2 要让其他 skill 能稳定接入。

### 13.1 三层集成级别

#### Level 1: Read-only

适合：

- review skill

只读：

- `project-state.md`
- relevant `workstreams/*.md`

#### Level 2: Read + append

适合：

- build / docs / design 类 skill

可做：

- 读 current state
- append session
- 更新 todo

#### Level 3: Governance-aware

适合：

- 长周期复杂 skill

可做：

- sync workstream
- promote decision
- generate handoff
- participate in compaction

### 13.2 对现有仓库内 skill 的接入建议

#### `production-code-quality-review`

建议：

- V2 初期按 Level 1 接入
- review 前读 `project-state.md`
- 必要时读 relevant workstream
- 只在明确采纳结论后再进入 `decisions.md`

#### `zero-to-website-design`

建议：

- 按 Level 3 接入
- 设计和实施阶段维护自己的 workstream
- 重要设计决定 promote 为 decision
- 暂停时生成 handoff

## 14. V2 references 规划

V2 建议新增以下 references：

- `surface-contract.md`
- `update-triggers.md`
- `quality-rules.md`
- `integration-patterns.md`
- `workstream-template.md`
- `snapshot-schema.md`

## 15. V2 开发阶段拆分

### Phase 1: 核心 contract 固化

目标：

- 不新增复杂自动化
- 先把 contract 写清楚

交付：

- 更新 `SKILL.md`
- 新增 contract references

### Phase 2: workstream / snapshot 引入

目标：

- 建立大项目扩展能力

交付：

- 更新 `state-schema`
- 扩展 `init_memory.py`
- 增加 workstream / snapshot 模板

### Phase 3: 治理脚本落地

目标：

- 把提升、压缩、同步机制做成 deterministic helpers

交付：

- `snapshot_state.py`
- `sync_workstream.py`
- `promote_decision.py`
- `generate_handoff.py`

### Phase 4: 质量控制

目标：

- 防止 memory 漂移失控

交付：

- `memory_lint.py`
- `stale_todo_check.py`
- 对应回归测试

### Phase 5: 多 skill 集成

目标：

- 让 repo 内其他 skill 逐步接入 contract

交付：

- 接入模式文档
- 至少一个现有 skill 的试点接入方案

## 16. 测试策略

V2 测试应覆盖：

### 16.1 结构测试

- package presence
- required references
- required scripts

### 16.2 合同测试

- 文件 section 校验
- reference routing consistency
- required fields completeness

### 16.3 脚本行为测试

- init / repair
- snapshot generation
- workstream sync
- decision promotion
- handoff generation
- session compaction

### 16.4 冲突测试

- stale todo
- inconsistent state
- missing rationale
- invalid workstream state

## 17. 验收标准

V2 完成时应满足：

1. 新会话能快速恢复项目全局状态与关键 workstreams
2. 并行任务不再全部堆到 `todo.md` 和 `session-log.md`
3. handoff 可以半自动生成且可直接继续执行
4. decision 记录质量高于 V1
5. memory 可被 lint 检查并发现明显坏味道
6. 至少一个其他 skill 能按 contract 接入
7. 长周期项目下 memory 不会迅速膨胀失控

## 18. 风险与约束

### 18.1 风险

- 设计过重，失去 V1 的轻量优势
- references 膨胀，导致 skill 认知负担上升
- 自动化写入过多，损坏语义质量
- contract 复杂但其他 skill 不真正接入

### 18.2 缓解策略

- contract 先于脚本扩展
- 自动提取证据，谨慎自动写语义
- 全程保持 progressive disclosure
- 优先做一个小范围试点，而不是全面铺开

## 19. 结论

V2 的关键不是“再加更多记忆文件”，而是把 `best-project-memory` 从文档型连续性 skill 升级为治理型连续性中枢。

它的成败取决于三件事：

1. contract 是否清晰
2. governance scripts 是否克制而有用
3. 多 skill 接入是否真正发生

如果这三件事做好，V2 会成为这个仓库里最有平台属性的基础 skill 之一。
## Phase 5 Pilot Status - 2026-06-17

Phase 5 is implemented as a Level 1 integration pilot with `production-code-quality-review`.

Delivered in this stage:

- `production-code-quality-review/scripts/review_skill_lib.py` now reads `.codex-memory/` when present
- review context JSON now exposes a `project_memory` object
- markdown and compact review briefs now surface project-memory presence and relevant workstreams
- `review-context.schema.json` now includes the `project_memory` contract
- CLI and unit coverage were expanded to lock the new integration behavior in place

Guardrails kept in this pilot:

- integration is read-only
- review setup consumes project state and relevant workstream summaries, but does not mutate memory
- workstream matching is conservative and strips Markdown list markers plus common low-signal tokens

Validation completed:

- `python -m unittest discover E:\project\blog\awesome-skills\production-code-quality-review\tests -v`
- `python -m unittest discover E:\project\blog\awesome-skills\best-project-memory\tests -v`

Review outcome:

- the Phase 5 code was reviewed using the `production-code-quality-review` workflow
- follow-up fixes tightened workstream matching and cleaned memory-summary rendering before signoff

Recommended next step:

- choose between a Level 2 append/update integration for an existing skill or a second Level 1 integration target for broader contract proving
