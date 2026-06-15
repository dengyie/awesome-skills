# 故障排查

## `collect-review-context.py` 推荐的 references 和我预期不一样

常见原因：

- 改动文件没有暴露出你期待的技术栈信号
- 当前 working tree 太窄，没有触发对应 risk flag
- 仓库形态本身更像另一类项目

建议先看：

- `detected_stack`
- `risk_flags`
- `changed_files`

这三个字段基本能解释大部分路由结果。

## 简报里显示 `Base: HEAD`

这表示辅助脚本无法可靠推断更合适的分支比较目标，所以回退到了当前 working-tree scope。

这在下面几种情况是正常的：

- 全新仓库
- 仓库里没有 `origin/main` 或 `origin/master`
- 只有本地改动，没有合适的分支基线

## 仓库很脏，简报 scope 看起来太宽

这是有意设计的。skill 会把 staged、unstaged、untracked 文件都纳入工作区 scope。

如果 scope 太宽，可以这样做：

- 清理无关文件
- 只 stage 目标文件
- 重新运行 `collect-review-context.py`

## 为什么这个 skill 很在意 changed-line ranges？

因为它们能帮助抑制误报：

- 更容易判断问题是不是这次引入的
- 更不容易把已有问题误报成新增问题
- 最终 review 会更贴近实际 diff

## skill 推荐的 references 比我想象中少

通常这是故意的。现在 skill 更偏向少而精的 reference 集合，目的是降低加载成本和浏览噪音。

## `review-entrypoint.py` 很方便，但我还是想看原始数据

直接用：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

`review-entrypoint.py` 更偏向快速人工简报，`collect-review-context.py` 才是原始结构化入口。

## TypeScript 仓库只识别成了 `typescript`，没有 `frontend`

如果仓库更像 TypeScript 后端服务，而不是浏览器 UI 项目，这属于正常现象。路由逻辑会尽量区分前端信号和通用 TypeScript service 信号。

## 本地测试都过了，但 Codex 的 review 还是一般

这个 skill 在以下条件齐全时效果最好：

- 能访问仓库
- 能访问真实 diff 或 working tree
- 能看到附近实现上下文
- 能看到测试

如果你只给了一小段代码，review 仍然可以做，但结论自然会更低置信度。
