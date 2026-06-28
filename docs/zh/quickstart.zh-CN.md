# 快速开始

这页只负责一件事：用最短路径把一个 skill 安装到本地并让 Codex 识别它。

如果你还没有决定要装哪个 skill，先看 [Skill Matrix](../usage/skill-matrix.md)。

## 1. 先选一个 skill

当前仓库里常用的包有：

- `best-project-memory`
- `evidence-driven-bugfix`
- `little-lighthouse-blog-publisher`
- `production-code-quality-review`
- `split-image-assets`
- `zero-to-website-design`

如果你不确定该选哪个，回到 [Skill Matrix](../usage/skill-matrix.md) 先做选型。

## 2. 安装一个 skill

当前 OpenAI Codex 文档常见安装路径：

- 用户级：`$HOME/.agents/skills`
- 仓库级：`.agents/skills`

安装一个包的最短方式：

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

把 `<skill-folder>` 替换成你要安装的 skill 目录名，例如 `evidence-driven-bugfix`。

## 3. 重新加载 Codex

复制完成后：

- 重启 Codex，或
- 在新会话里重新加载 skills

目标就是让 Codex 重新扫描已安装的 skill 目录。

## 4. 验证是否生效

开一个新会话，直接用 skill 名称提示，例如：

```text
Use $evidence-driven-bugfix to fix this failure by first capturing failing evidence and tracing the root cause.
```

如果 Codex 能识别这个 skill 名称，说明安装已经生效。

## 5. 继续往下走

- 还在选 skill： [Skill Matrix](../usage/skill-matrix.md)
- 想看中文仓库入口： [中文说明](README.zh-CN.md)
- 遇到问题： [故障排查](troubleshooting.zh-CN.md)
- 想看仓库常用路径： [黄金路径](golden-path.zh-CN.md)
