# Awesome Skills 中文说明

这是 `awesome-skills` 仓库的中文总览页。

仓库当前不是单一 skill，而是一个多 skill 集合，重点提供面向真实项目交付的 Codex 工作流能力。

当前包含 3 个已交付 skill：

- `best-project-memory`：项目记忆、进度恢复、决策记录、交接延续
- `production-code-quality-review`：面向生产环境的代码审查与合并前把关
- `zero-to-website-design`：从模糊需求到设计落地的网站工作流

英文版 `README.md` 仍然是默认入口；本页用于帮助中文使用者快速了解仓库结构、技能用途和后续阅读路径。

## 仓库包含哪些 Skill

### `best-project-memory`

这个 skill 用于让 Codex 在项目任务开始前先恢复上下文，并把关键信息持续写回仓库内的记忆文件，例如当前目标、阶段状态、待办项、会话摘要和关键决策。

适合场景：

- 跨会话延续项目工作
- 在仓库里保留可追溯的项目状态
- 维护长期 TODO 与里程碑
- 输出简洁的交接摘要
- 作为其他 skill 的连续性底座

入口文件：

```text
best-project-memory/SKILL.md
```

相关文档：

- [`docs/usage/best-project-memory.md`](../usage/best-project-memory.md)
- [`README.md`](../../README.md)

### `production-code-quality-review`

这个 skill 用于让 Codex 以生产工程视角审查代码改动、工作树 diff、PR 和架构敏感变更。它优先关注正确性、稳健性、可维护性、可观测性、测试充分性与误报控制，而不是停留在表面风格建议。

适合场景：

- PR 审查
- 合并前风险检查
- 高风险改动评估
- 生产发布前质量把关
- 需要结构化 review 上下文的审查流程

入口文件：

```text
production-code-quality-review/SKILL.md
```

相关文档：

- [`production-code-quality-review/README.md`](../../production-code-quality-review/README.md)
- [`review-workflows.zh-CN.md`](review-workflows.zh-CN.md)

### `zero-to-website-design`

这个 skill 用于把一个空白或模糊的网站需求推进成完整交付流程，包括视觉参考、设计方案、路线拆解、实现指引、截图验证和交付前检查。

适合场景：

- 从 0 到 1 的网站设计与实现
- 先设计文档、后代码落地
- 多页面路线规划
- 基于参考图的视觉方向控制
- 桌面端与移动端截图验收

入口文件：

```text
zero-to-website-design/SKILL.md
```

相关文档：

- [`docs/usage/zero-to-website-design.md`](../usage/zero-to-website-design.md)
- [`quickstart.zh-CN.md`](quickstart.zh-CN.md)

## 推荐阅读入口

中文优先入口：

- [中文快速开始](quickstart.zh-CN.md)
- [黄金路径](golden-path.zh-CN.md)
- [审查工作流](review-workflows.zh-CN.md)
- [示例](examples.zh-CN.md)
- [常见问题](faq.zh-CN.md)
- [故障排查](troubleshooting.zh-CN.md)
- [References 导读](references-guide.zh-CN.md)
- [中文发布说明](releases/README.zh-CN.md)

英文关键入口：

- [`README.md`](../../README.md)
- [`docs/usage/best-project-memory.md`](../usage/best-project-memory.md)
- [`docs/usage/zero-to-website-design.md`](../usage/zero-to-website-design.md)
- [`docs/usage/quickstart.md`](../usage/quickstart.md)
- [`docs/usage/golden-path.md`](../usage/golden-path.md)
- [`docs/usage/review-workflows.md`](../usage/review-workflows.md)
- [`docs/releases/README.md`](../releases/README.md)

## 使用建议

- 如果你首先关心“仓库里到底有什么”，先读英文 `README.md`
- 如果你要把 skill 安装到本地，优先看对应 skill 的入口目录和安装说明
- 如果你要理解审查工作流，优先看 `production-code-quality-review`
- 如果你要理解项目连续性与记忆文件流转，优先看 `best-project-memory`
- 如果你要做网站类项目交付，优先看 `zero-to-website-design`
