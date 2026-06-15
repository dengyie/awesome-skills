# 常见问题

## 为什么这个 skill 在 review 之前要先收集 repo context？

因为 review 质量非常依赖 scope。如果没有确定性的上下文，Codex 更容易：

- 把无关的工作区文件算进来
- 把已有问题误判成这次改动引入
- 在没有 changed-line 证据的情况下夸大结论

## 什么场景下应该用 `collect-review-context.py`？

当你需要机器可读的 review scope，或者要把结构化数据交给其他工具时，就应该用它。

## 什么场景下应该用 `review-entrypoint.py`？

当你想在正式让 Codex 全量审查前，先拿到一份适合人读的简报时，就用它。

## 为什么 references 文件变少了？

这是为了降低维护成本。现在的 references 保留了价值最高的拆分，同时减少了浏览和路由开销。

## 为什么还保留一些小脚本？

因为这些脚本是很实用的自动化积木。虽然多数用户只需要：

- `collect-review-context.py`
- `review-entrypoint.py`

但其他脚本依然适合更细粒度的集成场景。

## 这个 skill 能代替人工 code review 吗？

不能。它的目标是提升 review 质量、减少误报，而不是替代工程判断。最强的使用方式，仍然是把它当作人工 review 前后的一层生产级辅助。

## 现在 prompt 文件更少了，“specialist review lenses” 还成立吗？

成立。它现在表示 skill 仍然会从多个视角去分析改动：

- correctness
- architecture
- reliability
- security
- tests

结构更轻，但审查姿态还在。
