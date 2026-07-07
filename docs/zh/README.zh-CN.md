# Awesome Skills 中文说明

这是 `awesome-skills` 的中文入口页，目标是帮你先回答三件事：

- 这个仓库里有什么
- 我该先用哪个 skill
- 接下来该去看哪篇文档

## 仓库定位

这个仓库不是单一 skill，而是一组可复用的 Codex skill 包，重点面向证据优先、生产导向的真实项目工作流。

当前包含 7 个主要 skill：

- `best-project-memory`
- `codex-agent-worktree-setup`
- `evidence-driven-bugfix`
- `little-lighthouse-blog-publisher`
- `production-code-quality-review`
- `split-image-assets`
- `zero-to-website-design`

英文 GitHub 首页仍然是默认入口：[`README.md`](../../README.md)。

## 选择 Skill

| Skill | 何时使用 | 最适合处理 | 文档 |
| --- | --- | --- | --- |
| `best-project-memory` | 需要跨会话保存项目状态 | 上下文恢复、决策记录、TODO 和交接 | [Guide](../usage/best-project-memory.md) |
| `codex-agent-worktree-setup` | 需要创建 Codex UI 可见且绑定分支的 agent | 新线程、独立 worktree、分支固定、detached HEAD 修复 | [Skill](../../codex-agent-worktree-setup/SKILL.md) |
| `evidence-driven-bugfix` | 需要先拿失败证据再修 bug | 日志排查、根因定位、修复后复验 | [Guide](../usage/evidence-driven-bugfix.md) |
| `little-lighthouse-blog-publisher` | 需要发布 Little Lighthouse 博客内容 | 文章包创建、元数据确认、发布校验 | [Guide](../usage/little-lighthouse-blog-publisher.md) |
| `production-code-quality-review` | 需要从生产工程视角审查改动 | PR review、合并前把关、风险判断 | [审查工作流](review-workflows.zh-CN.md) |
| `split-image-assets` | 需要把单张图拆成可复用资产包 | mask、透明图层、预览、metadata、QA | [Guide](../usage/split-image-assets.md) |
| `zero-to-website-design` | 需要从模糊网站需求走到交付 | 视觉方向、路由规划、实现与 QA | [Guide](../usage/zero-to-website-design.md) |

如果你还不确定该选哪个，优先看 [Skill Matrix](../usage/skill-matrix.md)。

## 推荐起点

- 不知道该选哪个 skill： [Skill Matrix](../usage/skill-matrix.md)
- 想先快速安装一个 skill： [中文快速开始](quickstart.zh-CN.md)
- 想看英文原版首页： [`README.md`](../../README.md)
- 想先看仓库常用路径： [黄金路径](golden-path.zh-CN.md)

## 安装

当前 OpenAI Codex 文档常见安装路径：

- 用户级：`$HOME/.agents/skills`
- 仓库级：`.agents/skills`

安装一个 skill 的最短方式：

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

把 `<skill-folder>` 替换成你要安装的包名，例如 `evidence-driven-bugfix`。

更完整的安装入口看 [中文快速开始](quickstart.zh-CN.md)。

## 文档导航

- [中文快速开始](quickstart.zh-CN.md)
- [Skill Matrix](../usage/skill-matrix.md)
- [常见问题](faq.zh-CN.md)
- [故障排查](troubleshooting.zh-CN.md)
- [审查工作流](review-workflows.zh-CN.md)
- [示例](examples.zh-CN.md)
- [中文发布说明](releases/README.zh-CN.md)

说明：

- `Skill Matrix` 和大多数 skill 深页目前以英文为主
- 进入英文页时，skill 名称、命令、路径保持不翻译

## 仓库结构

```text
best-project-memory/                 skill 包
codex-agent-worktree-setup/          skill 包
evidence-driven-bugfix/             skill 包
little-lighthouse-blog-publisher/   skill 包
production-code-quality-review/     skill 包
split-image-assets/                 skill 包
zero-to-website-design/             skill 包
docs/usage/                         英文 usage 与导航页
docs/zh/                            中文入口与辅助文档
docs/releases/                      发布说明
docs/superpowers/                   设计文档与实现计划
tests/                              仓库级回归测试
```

## 维护者入口

- 仓库级文档检查：`python3 -m unittest discover tests -v`
- 发布历史入口：[`docs/releases/README.md`](../releases/README.md)
- 中文发布说明：[`releases/README.zh-CN.md`](releases/README.zh-CN.md)
- 设计与开发历史主要保存在 `docs/superpowers/` 和 `docs/dev/`
