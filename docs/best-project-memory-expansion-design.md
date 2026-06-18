# best-project-memory 扩展设计文档

## 1. 背景

`best-project-memory` 目前是一个极轻量的项目记忆 skill：它只约定在仓库内使用 `.codex-memory/` 下的四个 Markdown 文件来保存项目状态、会话日志、决策记录和待办事项。

它的优势是低摩擦、可审计、容易恢复上下文；但它也有明显短板：

- 只有存储约定，没有状态模型
- 只有追加日志，没有压缩与归档
- 只有记忆容器，没有检索与整理机制
- 只适合单人/单会话的“记一点东西”，不够支撑长期项目协作

本文档定义一个可扩展版本，把它升级为“项目连续性控制层”。

## 2. 目标

### 2.1 核心目标

1. 提升跨会话恢复上下文的速度和准确性
2. 让关键决策具备可追溯性
3. 让任务状态始终可见、可更新、可交接
4. 让其它 skill 可以统一读取和写入项目记忆

### 2.2 非目标

- 不把它做成数据库
- 不引入复杂外部服务
- 不替代 git 历史
- 不写长篇流水账

## 3. 设计原则

1. 轻量优先：默认保持 Markdown + 仓库内文件
2. 结构稳定：文件结构固定，字段语义固定
3. 追加优先：历史信息尽量不删，只做归档和摘要
4. 证据导向：关键结论尽量绑定文件、提交、测试或命令
5. 低上下文成本：SKILL.md 保持短，细节下沉到 references

## 4. 现状问题

### 4.1 只有四个文件，但职责不够细

- `project-state.md` 现在只能做快照，但还没有明确字段
- `session-log.md` 容易退化为聊天记录
- `decisions.md` 容易只记结论，不记依据
- `todo.md` 容易失去优先级与阶段感

### 4.2 缺少压缩机制

随着会话变长，session 日志会越来越厚，但没有阶段总结、归档、过期清理规则。

### 4.3 缺少协作协议

其它 skill 不知道应该如何读取、更新这些记忆文件，也不知道写入边界在哪里。

## 5. 扩展方案

### 5.1 文件层升级

继续保留原始四文件，但强化语义：

#### `project-state.md`

定位：当前项目的唯一“运行面板”

建议字段：

- Objective
- Current Phase
- Current Branch
- Last Verified
- Active Risks
- Active Blockers
- Current Focus
- Next Milestone
- Key Artifacts

#### `session-log.md`

定位：按时间记录的工作片段

建议字段：

- Task
- Actions
- Results
- Next
- Blockers

#### `decisions.md`

定位：ADR-lite 决策记录

建议字段：

- Decision
- Rationale
- Alternatives considered
- Impact
- Rollback trigger
- Related files

#### `todo.md`

定位：活跃任务清单

建议分区：

- In Progress
- Next
- Done

### 5.2 增加阶段记忆

建议新增：

- `.codex-memory/phases/`
- `.codex-memory/handoffs/`

用途：

- `phases/` 记录里程碑总结
- `handoffs/` 记录交接摘要

### 5.3 增加脚本层

建议新增 `scripts/`：

- `init_memory.py`：初始化记忆结构
- `append_session.py`：追加会话条目
- `snapshot_state.py`：生成当前状态摘要
- `handoff_pack.py`：生成交接包
- `stale_todo_check.py`：检查长期未更新任务

### 5.4 增加 references 层

建议新增 `references/`：

- `state-schema.md`：定义各文件字段
- `update-policy.md`：定义写入规则
- `examples.md`：给出高质量样例
- `handoff-patterns.md`：定义交接模式

## 6. 工作流

### 6.1 启动流程

1. 读取 `.codex-memory/` 的四个核心文件
2. 汇总当前目标、风险、阻塞、待办
3. 如果存在阶段文档，再读取阶段总结
4. 形成简短“loaded context”再继续任务

### 6.2 工作中更新流程

1. 小进展写 `session-log.md`
2. 决策写 `decisions.md`
3. 任务状态写 `todo.md`
4. 项目面板只保留最新摘要

### 6.3 收尾流程

1. 更新 `project-state.md`
2. 追加一条 session 结尾记录
3. 归纳新增 decision
4. 清理或推进 TODO
5. 必要时写阶段总结或交接包

## 7. 与其它 skill 的协同

### 7.1 可复用场景

- 代码审查前读取项目状态
- 设计实施前写入决策
- 长任务切换时生成交接包
- 发布前更新最后验证结果

### 7.2 约定边界

- skill 只负责读写 `.codex-memory/`
- 不强制其它 skill 修改自身逻辑
- 但鼓励其它 skill 引用统一状态文件

## 8. 建议实现优先级

### Phase 1

- 强化四个核心文件模板
- 明确每个文件的职责边界
- 在 SKILL.md 中写清楚启动/更新/收尾流程

### Phase 2

- 增加 `references/` 规范
- 增加 `handoffs/` 和 `phases/`

### Phase 3

- 增加 `scripts/`
- 把重复操作半自动化

### Phase 4

- 让其它 skill 统一接入
- 将它升级为仓库级连续性层

## 9. 验收标准

1. 新会话能在 30 秒内恢复关键上下文
2. 关键决策都有理由和影响范围
3. TODO 能反映真实当前工作，不堆积废项
4. 长会话结束后能自然产出交接包
5. 其它 skill 能在不读完整聊天记录的情况下继续工作

## 10. 结论

`best-project-memory` 最有价值的方向，不是扩大“记忆文本量”，而是形成一套稳定的项目连续性协议。

它应该从“本地笔记型 skill”升级为“仓库内状态中枢”。
