# 快速开始

`production-code-quality-review` 的目标，是让 Codex 用生产工程视角审查代码，同时把结论建立在确定性的仓库上下文上。

## 1. 安装 Skill

当前 OpenAI Codex 文档推荐的路径是：

- 用户级：`$HOME/.agents/skills`
- 仓库级：`.agents/skills`

手动安装：

```bash
mkdir -p ~/.agents/skills
cp -R production-code-quality-review ~/.agents/skills/
```

然后重启 Codex，或者重新加载 skills。

也可以直接使用辅助脚本：

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

该脚本默认安装到 `~/.agents/skills`。如果你明确需要第二份旧路径副本，再设置 `INSTALL_LEGACY_CODEX_COPY=1`。
安装后的副本也会记录来源仓库路径，方便 `update-local-skill.sh` 回到原始 checkout 做安全更新。

## 2. 收集 Review 上下文

运行：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

它会输出 JSON，包含：

- base branch 或 fallback scope
- staged、unstaged、untracked 文件
- changed files
- changed-line ranges
- detected stack
- risk flags
- suggested references
- safe verification commands

## 3. 生成 Review 简报

运行：

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
```

它会生成一份适合人阅读的简报，通常包括：

- scope 摘要
- review routing mode
- 建议加载的 references
- changed-line 范围摘要
- 推荐验证命令

## 4. 在 Codex 中调用 Skill

可以这样提示 Codex：

```text
Use $production-code-quality-review to review this change for production correctness and merge readiness.
```

如果 Codex 能访问本地仓库、diff 和测试，上述 skill 的效果会更稳定。

## 5. 验证 Skill 包

运行：

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

这会验证 deterministic helper 的核心行为。

如果你想用一条命令跑完主要发布检查，可以运行：

```bash
bash production-code-quality-review/scripts/verify-release.sh
```

这个 bundle 还会输出 `run-safe-checks.py` 提供的非破坏性验证建议。
