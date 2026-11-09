<!-- markdownlint-disable-file MD033 MD045 -->
<div align="center">

# Awesome Skills

**遵循 Agent Skills 开放规范的工业级智能体技能生态与工程工作流矩阵**

[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![LINUX DO](https://img.shields.io/badge/Community-LINUX%20DO-2563eb.svg?logo=linux&logoColor=white)](https://linux.do/)
[![Specification](https://img.shields.io/badge/Spec-Agent_Skills-8A2BE2.svg?style=flat-square)](https://docs.anthropic.com/)
[![Runtime Compatibility](https://img.shields.io/badge/Runtime-Codex_%7C_Claude_Code_%7C_ZCode_%7C_Cursor-blueviolet.svg?style=flat-square)]()
[![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen.svg?style=flat-square)]()

[English](./README.md) · [简体中文](./README.zh-CN.md) · [选择 Skill](#选择-skill) · [设计原则](#架构设计与核心原则) · [快速上手](docs/usage/quickstart.md) · [技能路由矩阵](docs/usage/skill-matrix.md) · [安装指引](#安装)

<br>

<p align="center">
  <b>彻底终结多智能体工程工作流中上下文窗口过度膨胀与提示词碎片化的混乱困境。</b><br>
  严格遵循开放 Agent Skills 规范构建，具备约 100-token 极简发现指纹、分支绑定的独立 Git 工作树与确定性失败证据复验门禁。<br>
  提供 17 个经生产环境严苛验证的模块化 Skill，覆盖证据驱动缺陷修复、跨 NAT 设备隧道穿透、Apple Liquid Glass 视效以及工业级代码审查。
</p>

</div>

---

## 致谢：LINUX DO

本项目致谢 [LINUX DO](https://linux.do/) 社区。自动化排障复验逻辑、工程评审标准以及跨 NAT 网络穿透等方案中的技术实现，主要参考了 LINUX DO 社区的技术讨论与方案分享。

---

## 痛点与架构对比

智能体技能生态常陷入两种极端：要么是冗长庞大的单体提示词文件，在初次加载时便吃满宝贵的上下文窗口；要么是缺乏标准化元数据与测试用例的散落脚本，无法跨平台迁移且极易出错。Awesome Skills 依托渐进式披露与独立沙盒设计实现了架构平衡：

| 评估维度 | Awesome Skills 技能生态 | 传统散落提示词模板 | 庞大重型单体智能体框架 |
| :--- | :--- | :--- | :--- |
| **Token 损耗** | 初次检索仅暴露约 100-token 元数据，按需载入正文 | 无条件塞入数千 token 冗长说明 | 系统级 Prompt 沉重，框架层开销高 |
| **执行隔离性** | 绑定 Git 独立工作树 (`codex-agent-worktree-setup`) | 在未提交的脏工作区直接运行，极易覆盖代码 | 强依赖重型 Docker 容器或全虚拟化沙箱 |
| **缺陷修复纪律** | 改动前强制捕获确定性失败证据 (`evidence-driven-bugfix`) | 盲目猜测修改，缺乏自动化复验闭环 | 依靠试错循环，无结构化证据链存证 |
| **底层硬件协同** | 原生 Apple Liquid Glass、FRP STCP、EasyTier 网格、Android JNI | 仅限简单的 Web 抓取或文本处理脚本 | 强行绑定特定厂商云端闭源基础设施 |
| **测试与质量守护** | 完备单元测试套件 + 仓库级文档契约断言门禁 | 零自动化测试与格式校验 | 维护复杂的多层端到端集成测试底座 |

---

## 架构设计与核心原则

- **改动前必须先抓取复现证据**：`evidence-driven-bugfix` 与 `production-code-quality-review` 要求先拿到确定性失败证据并定位根因，再修改代码并复验。
- **渐进式加载控制上下文开销**：每个模块遵循标准规范，初次检索时仅暴露元数据，占用约 100 tokens；操作脚本与参考资料仅在调用时按需读取。
- **隔离执行防止污染主工作区**：`codex-agent-worktree-setup` 把 Agent 执行流程绑定到独立的 Git worktree，避免分支状态影响主工作目录。
- **独立解耦支持按需引入**：所有模块均为自包含结构，各自维护说明文档、参考规范与可选的执行脚本。

---

## 技能分类导航

### 软件工程与质量保证

- [`evidence-driven-bugfix`](evidence-driven-bugfix/): 捕获确定性失败证据，准确定位根因，并在修复后执行严格复验。
- [`production-code-quality-review`](production-code-quality-review/): 从生产工程视角审查 Pull Request、评估合并风险与敏感差异。
- [`codex-agent-worktree-setup`](codex-agent-worktree-setup/): 为 Agent 执行线程创建与分支绑定的隔离 Git 工作树。
- [`best-project-memory`](best-project-memory/): 跨会话沉淀项目核心上下文、关键架构决策与交接状态。

### 网络通信与基础设施运维

- [`cloudphone-adb-tunnel`](cloudphone-adb-tunnel/): 配置 FRP STCP 隧道与 Termux 保活，实现公网对无 root 安卓云手机的 ADB 调试与 scrcpy 投屏。
- [`windows-ssh-stcp`](windows-ssh-stcp/): 经由现有 FRP STCP 中继安全接入 NAT 内网 Windows 主机，配合 NSSM 保活。
- [`cue-sandbox`](cue-sandbox/): 经 EasyTier TUN SSH 接入 Cue 沙盒，配备印度反向 SSH 兜底与 Komari 探针。
- [`muse-reverse-ssh`](muse-reverse-ssh/): 建立反向 SSH 隧道与 VPS 端口转发管道，具备全自动保活看门狗。
- [`render-engine`](render-engine/): 引导从零在 Render 免费层部署非特权 Linux 容器，集成 Caddy 复用与 ttyd+tmux 持久会话。

### UI 工程与图形资产处理

- [`awesome-ui-kit`](awesome-ui-kit/): 提供开箱即用的 AI 对话、RAG 检索呈现、Canvas 分屏与 Agent 监控原子 Web 组件。
- [`gpui-liquid-glass`](gpui-liquid-glass/): 在 Rust GPUI 桌面端实现与调试 Apple 原生液体玻璃质感与毛玻璃混合视效。
- [`split-image-assets`](split-image-assets/): 将单张图像智能拆分为带 Alpha 透明蒙版的标准化工程资产包。

### 联网检索、知识库与自动化

- [`grok-search`](grok-search/): 聚合联网实时搜索、深度内容提取与站点结构化候选页发现。
- [`huawei-cloud-gallery-publish`](huawei-cloud-gallery-publish/): CodeArts ACP 一键生成网页并自动发布至华为云开发者作品展览馆。
- [`obsidian-doc-router`](obsidian-doc-router/): 提供知识库路由查询与防孤岛闭环工作流，统一管理运维拓扑与架构事实。
- [`phone-playwright`](phone-playwright/): 移动端 Playwright 式自动化框架与手机端 AI Agent 执行引擎。
- [`yunzhi-cloudphone-checkin`](yunzhi-cloudphone-checkin/): 云智手机每日自动签到与云机空间权益自动化续期套件。

---

## 选择 Skill

| Skill | 何时使用 | 最适合处理 | 文档 |
| --- | --- | --- | --- |
| `awesome-ui-kit` | 需要组装 AI 聊天、RAG、Canvas 分屏或 Agent 控制台页面 | 复制即用 AI 网页原子组件、多前端框架对齐 | [Guide](docs/usage/awesome-ui-kit.md) |
| `best-project-memory` | 需要跨会话保存项目状态 | 上下文恢复、决策记录、TODO 和交接 | [Guide](docs/usage/best-project-memory.md) |
| `cloudphone-adb-tunnel` | 需要从公网远程 ADB/投屏无 root 云手机 | FRP STCP 隧道、Termux frpc 保活、Android 13 加固 | [Guide](docs/usage/cloudphone-adb-tunnel.md) |
| `codex-agent-worktree-setup` | 需要创建与分支绑定的隔离 Codex 工作线程 | 保护主工作树、创建隔离 agent、修复 detached HEAD | [Guide](docs/usage/codex-agent-worktree-setup.md) |
| `cue-sandbox` | 需要把无公网入站的 Cue 接到 EasyTier mesh SSH，印度反向 SSH 只作兜底 | TUN `.81`、两把钥、Komari 探针、overlay 挖矿 | [Guide](docs/usage/cue-sandbox.md) |
| `evidence-driven-bugfix` | 需要先拿失败证据再修 bug | 日志排查、根因定位、修复后复验 | [Guide](docs/usage/evidence-driven-bugfix.md) |
| `gpui-liquid-glass` | 需要在 Rust GPUI 桌面应用中实现或调试 Apple 原生液体玻璃与毛玻璃材质 | NSGlassEffectView、vibrancy 降级、透明窗口与 Metal 合成、布局几何同步 | [Guide](docs/usage/gpui-liquid-glass.md) |
| `grok-search` | 需要联网搜索、抓取网页或发现站点页面 | 最新事实核查、URL 正文抓取、站点候选页发现 | [Guide](docs/usage/grok-search.md) |
| `huawei-cloud-gallery-publish` | 需要把简单网页一键发布到华为云开发者作品展览馆 | CodeArts ACP 生成页面、开发隧道、GitCode 推送、一次确认投递闯关活动 | [Guide](docs/usage/huawei-cloud-gallery-publish.md) |
| `muse-reverse-ssh` | 需要让无公网 IP 的机器从公网经 SSH 访问 | 反向 SSH 隧道、VPS 端口转发、隧道保活 | [Guide](docs/usage/muse-reverse-ssh.md) |
| `obsidian-doc-router` | 需要查阅或记录 Obsidian 知识库运维事实与拓扑 | 权威路由表首查、防孤岛文档闭环记录 | [Guide](docs/usage/obsidian-doc-router.md) |
| `phone-playwright` | 需要移动端 Playwright 式自动化或构建手机 AI Agent | 视口语义蒸馏、可用性自动等待、温热缓存极速首击、MCP 服务端 | [Guide](docs/usage/phone-playwright.md) |
| `production-code-quality-review` | 需要从生产工程视角审查改动 | PR review、合并前把关、风险判断 | [审查工作流](docs/usage/review-workflows.md) |
| `render-engine` | 需要从 0 引导注册 Render、Fork 代码、部署容器与连接终端 | 零门槛注册引导、Blueprint 一键部署、ttyd+tmux 持久化会话 | [Guide](docs/usage/render-engine.md) |
| `split-image-assets` | 需要把单张图拆成可复用资产包 | mask、透明图层、预览、metadata、QA | [Guide](docs/usage/split-image-assets.md) |
| `windows-ssh-stcp` | 需要 SSH 登录一台没有公网入站端口的 Windows | 复用已有 frps 的 STCP、只听环回的 sshd、NSSM 保活 | [Guide](docs/usage/windows-ssh-stcp.md) |
| `yunzhi-cloudphone-checkin` | 需要云智手机每日签到与云机空间自动续期 | 浏览器控制台一键脚本、Chrome CDP 无感自动化、直连 CLI | [Guide](docs/usage/yunzhi-cloudphone-checkin.md) |

如果你还不确定该选哪个，优先查阅 [Skill Matrix](docs/usage/skill-matrix.md)。

---

## 推荐起点

- 我不知道该选用哪款 Skill：[Skill Matrix](docs/usage/skill-matrix.md)
- 我希望以最快速度安装使用：[快速开始](docs/usage/quickstart.md)
- 我希望查阅进阶工作流：[Golden Path](docs/usage/golden-path.md)
- 我需要执行生产代码评审：[审查工作流](docs/usage/review-workflows.md)
- 我希望查阅真实落地样例：[使用样例](docs/usage/examples.md)

---

## 安装

Skill 自动发现路径取决于所使用的宿主客户端环境：

| 客户端 | 用户全局作用域 | 工作区本地作用域 |
| --- | --- | --- |
| OpenAI Codex / ZCode | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor / Windsurf / Gemini CLI | `~/.agents/skills/` | `.agents/skills/` |

### 快速安装命令

将选定的 Skill 目录完整复制到宿主发现路径中：

```bash
mkdir -p ~/.agents/skills
cp -R <skill-folder> ~/.agents/skills/
```

完成复制后重启客户端或重新加载技能列表即可生效。

### 标准包结构规范

每个 Skill 均严格遵循标准化目录布局：

```text
<skill-name>/
├── SKILL.md          # 核心元数据（Frontmatter）与执行指令
├── scripts/          # 确定性自动化脚本与 CLI 入口
├── references/       # API 规范与深入技术参考文档
└── assets/           # 配置文件、静态模版与资源资产
```

---

## 文档导航

- [快速开始](docs/usage/quickstart.md) — 快速安装与验证指南
- [Skill Matrix](docs/usage/skill-matrix.md) — 全量功能矩阵与路由导航表
- [常见问答 (FAQ)](docs/usage/faq.md) — 高频疑问与技术细节答疑
- [故障排查 (Troubleshooting)](docs/usage/troubleshooting.md) — 运行异常诊断与解决方案
- [审查工作流](docs/usage/review-workflows.md) — 生产级代码审查流程与规范
- [落地案例](docs/usage/examples.md) — 典型生产落地场景演示
- [中文专题总览](docs/zh/README.zh-CN.md) — 简体中文深度导览专区
- [更新日志](docs/releases/README.md) — 历史版本演进与发布说明

---

## 仓库结构

```text
awesome-ui-kit/                     AI 对话、RAG 检索呈现、思维链与分屏 Canvas 组件库
best-project-memory/                跨会话项目记忆、决策追溯与交接状态存证
cloudphone-adb-tunnel/              基于 FRP STCP 的免 root 安卓云手机 ADB/scrcpy 隧道
codex-agent-worktree-setup/         与分支绑定的 Agent 隔离 Git 工作树管理套件
cue-sandbox/                        基于 EasyTier TUN 的 SSH 接入与 Komari 探针集成
evidence-driven-bugfix/             证据优先的确定性缺陷复现与修复闭环
grok-search/                        实时联网检索、深度页面提取与站点候选页发现
huawei-cloud-gallery-publish/       CodeArts ACP 页面一键生成与华为云作品展快速发布
muse-reverse-ssh/                   反向 SSH 隧道与 VPS 端口转发自动化守护
obsidian-doc-router/                Obsidian 知识库路由查询与防孤岛运维文档流
phone-playwright/                   移动端 Playwright 式自动化测试与手机 AI Agent 引擎
production-code-quality-review/     生产级代码质量审计与合并就绪度评估
render-engine/                      Render 免费层非特权 Linux 容器部署、Caddy 与 ttyd
split-image-assets/                 单张图像透明图层分解、蒙版提取与工程化资产打包
windows-ssh-stcp/                   内网 Windows 主机经由 FRP STCP 的安全 SSH 接入
yunzhi-cloudphone-checkin/          云智手机每日自动化签到与云机空间权益续期
docs/usage/                         使用指南、选型矩阵、故障排查与落地案例
docs/zh/                            中文落地页与本地化深度技术文档
docs/releases/                      历史版本说明与更新日志
docs/superpowers/                   架构设计规范与演进规划
tests/                              仓库级自动化回归测试套件
```

---

## 参与贡献与维护者入口

- 提交代码前请确保执行仓库级文档测试：`python3 -m unittest discover tests -v`
- 发布前请进入对应 Skill 目录执行局部测试套件
- 保持 `docs/releases/README.md` 的更新记录同步
- 涉及架构与规范调整请同步更新 `docs/superpowers/`

本项目采用 [MIT License](LICENSE) 开源协议。
