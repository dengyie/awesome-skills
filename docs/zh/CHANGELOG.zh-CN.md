# 变更记录

这个文件是顶层 [`CHANGELOG.md`](../../CHANGELOG.md) 的中文补充版，帮助中文读者快速理解每个版本的主要变化。

英文版仍然是默认事实来源；当中英文有细微差异时，以英文原文为准。

## v0.1.2 - 2026-06-16

### 变更

- 本地安装脚本对齐到当前推荐的 `~/.agents/skills` 路径
- 将 `~/.codex/skills` 旧副本改为显式开关同步
- README 补充安装行为、`compact` 模式和仓库结构说明
- onboarding 文档明确辅助安装脚本的默认行为
- `update-local-skill.sh` 支持从已安装副本回到记录的来源 checkout 做刷新

### 移除

- 从发布产物中清理被跟踪的 Python cache 文件

## v0.1.1 - 2026-06-16

### 新增

- 黄金路径 onboarding 文档
- `review-entrypoint.py` 的 `compact` 输出模式
- 本地安装和更新辅助脚本
- release checklist 与 troubleshooting 文档
- 覆盖 TypeScript API、数据库迁移、Docker 场景的 fixture 风格测试

### 变更

- 收紧 `SKILL.md`，减少重复解释
- 改进 TypeScript service 仓库的 stack detection
- Python 默认验证命令调整为 `unittest discover`
- README 简化为更清晰的产品首页

## v0.1.0 - 2026-06-16

### 新增

- `production-code-quality-review` 从 review SOP 升级为可测试的 skill 包
- 确定性的 repo-context 脚本，用于：
  - review scope 收集
  - changed-line 映射
  - stack detection
  - markdown review brief 生成
- 更聚焦的 references 集，包括：
  - review framework
  - output contract
  - false-positive control
  - security
  - TypeScript
  - backend and integrations
  - verification and operations
  - database changes
- synthesis prompt 资产
- helper 行为的自动化测试
- 开发与发布文档

### 变更

- skill 结构进一步简化，便于维护
- README 更新为更偏产品说明的落地页
- 文档中明确主要用户入口

### 移除

- `references/language-specific.md`
- 过于分散的 reviewer prompt 结构
- 一些过度拆分的 reference 文件，改为更易维护的合并指南
