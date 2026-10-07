# Awesome Skills 中文说明

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![LINUX DO](https://img.shields.io/badge/Community-LINUX%20DO-2563eb.svg?logo=linux&logoColor=white)](https://linux.do/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

本仓库收录一系列遵循 Agent Skills 开放规范的独立模块，面向软件工程、生产运维、代码评审与前端交互开发场景。

英文主页：[`README.md`](../../README.md)

---

## 致谢：LINUX DO

本项目致谢 [LINUX DO](https://linux.do/) 社区。自动化排障复验逻辑、工程评审标准以及跨 NAT 网络穿透等方案中的技术实现，主要参考了 LINUX DO 社区的技术讨论与方案分享。

---

## 仓库定位

本仓库收录一组遵循 Agent Skills 规范的独立工程包，用于解决日常开发与运维中的具体技术问题。

当前包含 12 个核心 skill：

- `awesome-ui-kit`
- `best-project-memory`
- `cloudphone-adb-tunnel`
- `codex-agent-worktree-setup`
- `evidence-driven-bugfix`
- `grok-search`
- `muse-reverse-ssh`
- `obsidian-doc-router`
- `production-code-quality-review`
- `split-image-assets`
- `windows-ssh-stcp`
- `yunzhi-cloudphone-checkin`

英文 GitHub 首页仍然是默认入口：[`README.md`](../../README.md)。

---

## 核心设计原则

- 改动前必须先抓取复现证据：`evidence-driven-bugfix` 与 `production-code-quality-review` 要求先拿到确定性失败证据并定位根因，再修改代码并复验。
- 渐进式加载控制上下文开销：每个模块遵循标准规范，初次检索时仅暴露元数据，占用约 100 tokens；操作脚本与参考资料仅在调用时按需读取。
- 隔离执行防止污染主工作区：`codex-agent-worktree-setup` 把 Agent 执行流程绑定到独立的 Git worktree，避免分支状态影响主工作目录。
- 独立解耦支持按需引入：所有模块均为自包含结构，各自维护说明文档、参考规范与可选的执行脚本。

---

## 选择 Skill

| Skill | 何时使用 | 最适合处理 | 文档 |
| --- | --- | --- | --- |
| `awesome-ui-kit` | 需要组装 AI 聊天、RAG、Canvas 分屏或 Agent 控制台页面 | 复制即用 AI 网页原子组件、多前端框架对齐 | [Guide](../usage/awesome-ui-kit.md) |
| `best-project-memory` | 需要跨会话保存项目状态 | 上下文恢复、决策记录、TODO 和交接 | [Guide](../usage/best-project-memory.md) |
| `cloudphone-adb-tunnel` | 需要从公网远程 ADB/投屏无 root 云手机 | FRP STCP 隧道、Termux frpc 保活、Android 13 加固 | [Guide](../usage/cloudphone-adb-tunnel.md) |
| `codex-agent-worktree-setup` | 需要创建与分支绑定的隔离 Codex 工作线程 | 保护主工作树、创建隔离 agent、修复 detached HEAD | [Guide](../usage/codex-agent-worktree-setup.md) |
| `evidence-driven-bugfix` | 需要先拿失败证据再修 bug | 日志排查、根因定位、修复后复验 | [Guide](../usage/evidence-driven-bugfix.md) |
| `grok-search` | 需要联网搜索、抓取网页或发现站点页面 | 最新事实核查、URL 正文抓取、站点候选页发现 | [Guide](../usage/grok-search.md) |
| `muse-reverse-ssh` | 需要让无公网 IP 的机器从公网经 SSH 访问 | 反向 SSH 隧道、VPS 端口转发、隧道保活 | [Guide](../usage/muse-reverse-ssh.md) |
| `obsidian-doc-router` | 需要查阅或记录 Obsidian 知识库运维事实与拓扑 | 权威路由表首查、防孤岛文档闭环记录 | [Guide](../usage/obsidian-doc-router.md) |
| `production-code-quality-review` | 需要从生产工程视角审查改动 | PR review、合并前把关、风险判断 | [审查工作流](review-workflows.zh-CN.md) |
| `split-image-assets` | 需要把单张图拆成可复用资产包 | mask、透明图层、预览、metadata、QA | [Guide](../usage/split-image-assets.md) |
| `windows-ssh-stcp` | 需要 SSH 登录一台没有公网入站端口的 Windows | 复用已有 frps 的 STCP、只听环回的 sshd、NSSM 保活 | [Guide](../usage/windows-ssh-stcp.md) |
| `yunzhi-cloudphone-checkin` | 需要云智手机每日签到与云机空间自动续期 | 浏览器控制台一键脚本、Chrome CDP 无感自动化、直连 CLI | [Guide](../usage/yunzhi-cloudphone-checkin.md) |

如果你还不确定该选哪个，优先看 [Skill Matrix](../usage/skill-matrix.md)。

---

## 推荐起点

- 不知道该选哪个 skill： [Skill Matrix](../usage/skill-matrix.md)
- 想先快速安装一个 skill： [中文快速开始](quickstart.zh-CN.md)
- 想看英文原版首页： [`README.md`](../../README.md)
- 想先看仓库常用路径： [黄金路径](golden-path.zh-CN.md)
- 想了解生产代码审查： [审查工作流](review-workflows.zh-CN.md)
- 想看真实案例演示： [示例](examples.zh-CN.md)

---

## 安装

各 Agent 客户端通过扫描特定目录发现 Skill：

| 客户端 | 用户级目录 (User Scope) | 仓库级目录 (Workspace Scope) |
| --- | --- | --- |
| OpenAI Codex / ZCode | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor / Windsurf / Gemini CLI | `~/.agents/skills/` | `.agents/skills/` |

### 安装操作

把目标 Skill 目录复制到客户端检索路径中：

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

复制完成后，重启 Agent 或重新加载技能列表即可完成索引。

更完整的安装细节与排错参考 [中文快速开始](quickstart.zh-CN.md)。

### 模块目录结构

每个 Skill 统一遵循标准结构组织：

```text
<skill-name>/
├── SKILL.md          # 模块元数据与使用说明
├── scripts/          # 可执行脚本、校验工具与命令行入口
├── references/       # 接口规范、架构说明与参考资料
└── assets/           # 模板文件、配置文件与静态资产
```

---

## 文档导航

- [中文快速开始](quickstart.zh-CN.md) — 快速安装与配置入门
- [Skill Matrix](../usage/skill-matrix.md) — 全功能路由矩阵与选型对比
- [常见问题](faq.zh-CN.md) — 核心概念与日常 FAQ
- [故障排查](troubleshooting.zh-CN.md) — 异常处理与排障步骤
- [审查工作流](review-workflows.zh-CN.md) — 生产级代码评审标准指南
- [示例](examples.zh-CN.md) — 跨技能典型实战案例
- [中文发布说明](releases/README.zh-CN.md) — 历史版本演进与发布记录

说明：

- `Skill Matrix` 和大多数 skill 深页目前以英文为主
- 进入英文页时，skill 名称、命令、路径保持不翻译

---

## 仓库结构

```text
awesome-ui-kit/                     AI 对话、RAG、Canvas 分屏与 Agent 监控组件包
best-project-memory/                跨会话项目上下文保持、决策记录与交接
cloudphone-adb-tunnel/              非 root 安卓云手机 FRP STCP 远程 ADB 穿透包
codex-agent-worktree-setup/         与分支绑定的隔离 Codex 工作线程包
evidence-driven-bugfix/             先拿失败证据再定位根因的排障工作流包
grok-search/                        联网搜索、实时事实核查与网页发现包
muse-reverse-ssh/                   反向 SSH 隧道与 VPS 端口转发保活包
obsidian-doc-router/                Obsidian 知识库运维事实查阅与防孤岛闭环包
production-code-quality-review/     生产工程视角的 PR 审计与 diff 审查包
split-image-assets/                 单图拆解透明图层、mask 与元数据资产包
windows-ssh-stcp/                   无公网入站 Windows 的 FRP STCP SSH 穿透包
yunzhi-cloudphone-checkin/          云智手机每日签到与云机空间自动续期包
docs/usage/                         英文 usage 与导航页
docs/zh/                            中文入口与辅助文档
docs/releases/                      发布说明
docs/superpowers/                   设计文档与实现计划
tests/                              仓库级回归测试
```

---

## 维护者入口

- 仓库级文档检查：`python3 -m unittest discover tests -v`
- `grok-search/` 是 Grok Search 的维护源，本机 skill 安装目录仅作为下游副本
- 发布历史入口：[`docs/releases/README.md`](../releases/README.md)
- 中文发布说明：[`releases/README.zh-CN.md`](releases/README.zh-CN.md)
- 设计与开发历史主要保存在 `docs/superpowers/` 和 `docs/dev/`
