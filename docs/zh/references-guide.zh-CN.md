# References 导读

这份文档不是 `references/` 的逐字翻译，而是一份中文导读。

目的很简单：

- 帮中文团队快速理解每个 reference 是干什么的
- 帮使用者知道什么场景该读哪个 reference
- 保持英文原版仍然是唯一事实来源，降低双语维护成本

## 先理解 `references/` 是什么

`production-code-quality-review/references/` 里的文件，主要是给 skill 和 agent 用的“审查规则手册”。

它们不是 README 那种面向普通用户的介绍文档，而是更接近：

- 审查思维框架
- 输出格式约束
- 误报抑制规则
- 技术栈专项审查提示
- 运维与验证检查项

## 如何使用这些 references

一般不需要一次性全读。

更合理的方式是：

1. 先跑 `collect-review-context.py`
2. 看 `suggested_references`
3. 按需加载对应 reference

默认几乎总是有价值的三份：

- `review-framework.md`
- `output-contract.md`
- `false-positive-control.md`

## 每个 reference 的作用

### `review-framework.md`

这是总框架。

适合场景：

- 大一点的 diff
- 高风险改动
- 跨模块改动
- 架构敏感改动

它主要回答：

- review 应该按什么阶段进行
- scope 和 intent 怎么先确定
- correctness、robustness、architecture、tests 分别怎么看
- 什么 finding 该保留，什么该降级到 questions

如果只能读一份 reference，通常先读这份。

### `output-contract.md`

这是输出格式契约。

适合场景：

- 你想让 review 结果更稳定
- 你要把 review 输出接到别的工具里
- 你想减少“每次输出格式都不一样”的问题

它主要定义：

- Scope 段怎么写
- Findings 段需要哪些字段
- Questions、Architecture Assessment、Robustness Assessment、Test Assessment 怎么组织
- Final Recommendation 的可选结论

### `false-positive-control.md`

这是误报抑制手册，也是这个 skill 最关键的 reference 之一。

适合场景：

- 你担心 AI review 乱报问题
- 你要控制信任感
- 你要区分 confirmed / likely / speculative 问题

它主要强调：

- 没 location 不报
- 没 evidence 不报
- 没 realistic failure mode 不报
- low confidence 默认不要进主 findings
- pre-existing 问题不要当作本次改动正常 finding

如果团队最在意“少误报”，这份必须优先理解。

### `security.md`

这是安全、隐私、性能、可扩展性四合一 gate。

适合场景：

- 鉴权、授权
- 用户输入
- 文件、数据库、模板、shell、外部依赖
- PII、支付、网络请求
- 热路径、批处理、队列、缓存

它不是泛泛地说“注意安全”，而是要求有可达的 misuse path。

核心价值：

- 降低空泛安全焦虑
- 逼着 review 给出真实攻击路径或滥用路径
- 同时把 performance / scalability 也纳入现实约束

### `typescript.md`

这是 TypeScript / JavaScript / 前端共享契约的专项检查表。

适合场景：

- TypeScript 服务
- React 或前端界面
- 前后端共享类型
- shared runtime contract

它重点关注：

- runtime validation 是否真实存在
- `any`、unsafe cast、non-null assertion
- Promise rejection
- 类型和真实 payload 漂移
- UI 状态、effect、stale closure、loading/error/disabled 状态

如果你的主栈是 TS/JS，这份通常非常高频。

### `backend-and-integrations.md`

这是后端与集成类改动的专项检查表。

适合场景：

- Node 服务
- API route
- webhook
- queue / scheduler
- 外部 SDK client
- 跨服务契约

它主要检查：

- request / response boundary
- 幂等性
- timeout / retry / cancellation
- 外部调用失败时的局部一致性
- webhook 和 queue 的重复投递处理
- 关联日志、重试指标、请求链路定位

如果改动碰到了 API 和外部系统，这份通常应该加载。

### `database.md`

这是数据库与迁移专项检查表。

适合场景：

- schema
- migration
- query
- index
- transaction
- persistence logic

它最关注：

- rolling deploy 下的兼容性
- lock duration 和 blast radius
- rollback path
- 大表默认值和 backfill 风险
- transaction boundary
- tenant / workspace scope
- index coverage 和 N+1

涉及迁移时，这份优先级很高。

### `verification-and-operations.md`

这是测试质量和可运维性的专项检查表。

适合场景：

- 测试改动
- 背景任务
- 失败处理
- observability
- on-call 诊断能力

它会帮助你追问：

- 哪个测试真的会因为这个 bug 失败
- 出故障后 on-call 怎么发现
- 怎么定位受影响请求、用户、任务或记录
- 日志、指标、trace 是否足够

如果变更和测试、运维、故障诊断有关，这份很有用。

## 一个简单的选择方法

可以按下面这套快速选：

- 默认基础包：
  - `review-framework.md`
  - `output-contract.md`
  - `false-positive-control.md`
- TypeScript / 前端：
  - `typescript.md`
- 后端 API / 外部集成：
  - `backend-and-integrations.md`
- 数据库 / 迁移：
  - `database.md`
- 安全 / 支付 / PII / 热路径：
  - `security.md`
- 测试 / 日志 / 运维 / 故障处理：
  - `verification-and-operations.md`

## 实际建议

- 不建议维护整套中文 `references/` 镜像。
- 建议保留英文原版作为唯一事实来源。
- 中文层面保留这份“导读”就够了。

这样既能让团队看懂，也不会让双语维护成本失控。
