# Awesome Skills 中文说明

英文版仍然是默认版本，本目录提供 `production-code-quality-review` 的中文补充文档，方便中文使用者快速上手。

## 文档入口

- [快速开始](quickstart.zh-CN.md)
- [黄金路径](golden-path.zh-CN.md)
- [审查工作流](review-workflows.zh-CN.md)
- [示例](examples.zh-CN.md)
- [常见问题](faq.zh-CN.md)
- [故障排查](troubleshooting.zh-CN.md)
- [中文变更记录](CHANGELOG.zh-CN.md)
- [中文发布说明](releases/README.zh-CN.md)

## 适用对象

这套 skill 适合以下场景：

- 让 Codex 审查本地工作区改动
- 在提交前做一次生产级代码 review
- 审查高风险改动，例如鉴权、数据库迁移、支付、部署、容器运行时
- 为 PR、发布、交接生成稳定的 review scope 和检查建议

## 核心原则

- 默认英文原版优先，中文文档作为镜像补充
- 先收集确定性的 repo 上下文，再做结论
- 重点减少误报，而不是堆积泛泛而谈的意见
- 默认只读 review，不轻易把审查变成直接改代码

## 对应英文入口

如果你需要引用项目默认文档，请优先使用这些英文页面：

- [`README.md`](../../README.md)
- [`CHANGELOG.md`](../../CHANGELOG.md)
- [`docs/usage/quickstart.md`](../usage/quickstart.md)
- [`docs/usage/golden-path.md`](../usage/golden-path.md)
- [`docs/usage/review-workflows.md`](../usage/review-workflows.md)
- [`docs/usage/examples.md`](../usage/examples.md)
- [`docs/usage/faq.md`](../usage/faq.md)
- [`docs/usage/troubleshooting.md`](../usage/troubleshooting.md)
- [`docs/releases/release-checklist.md`](../releases/release-checklist.md)
