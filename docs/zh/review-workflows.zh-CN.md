# 审查工作流

这份文档说明 `production-code-quality-review` 的几种主要使用方式。

## 本地工作区审查

适用于你还没有提交代码，但想先对当前工作区做一次生产级 review。

建议流程：

1. 收集上下文：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

2. 生成 markdown 简报：

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

3. 让 Codex 用 skill 审查当前工作区：

```text
Use $production-code-quality-review to review my current working tree like a senior production engineer.
```

## 面向 Diff 的审查

适用于你更关心“相对于分支基线到底改了什么”，而不只是裸工作区文件。

脚本会自动推断 base branch；如果无法推断，就回退到 `HEAD`。之后 skill 会结合以下信息尽量抑制无关 finding：

- changed files
- changed-line ranges
- risk flags

如果需要强制指定审查基线或 scope，`review-entrypoint.py` 和 `collect-review-context.py` 都支持：

- `--base <ref>`
- `--scope branch`
- `--scope working_tree`

## 高风险改动审查

适用于以下改动：

- 鉴权或权限
- 支付、账单
- 数据库迁移
- 重试、超时、并发
- 部署和运行时打包

在这种场景下，skill 会倾向于用更偏专题化的审查视角来思考：

- correctness
- architecture
- reliability
- security
- tests

然后再合并为最终结论。

## 快速人工简报

如果你暂时不想做完整 review，只想快速看一下 scope 和风险方向，可以直接运行：

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

它适合用在这些场景：

- handoff
- code review 前准备
- PR 创建前
- release 检查前

## 机器可读自动化

如果你想把 repo context 提供给其他工具或自动化流程，推荐使用：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

这是最适合自动化的入口，因为它的 review scope 更可预测、结构也更稳定。
