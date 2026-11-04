---
name: obsidian-doc-router
description: >
  MANDATORY documentation router & best-practice-first pre-flight gate for the user's
  Obsidian vault and ANY engineering, ops, deploy, coding, onboarding, or configuration task.
  BEFORE executing any technical task, creating scripts, modifying architecture, or adding
  sites/channels/services, you MUST first lookup and inherit existing vault best practices,
  SOPs, and canonical specs (DO NOT reinvent the wheel or do redundant live testing).
  BEFORE answering ops questions or grepping blindly, you MUST consult 00.MOC/AI-DOC-ROUTER.md.
  WHENEVER writing/creating/modifying docs, strictly follow the Anti-Orphan Recording SOP.
  Triggers when: user mentions 最佳实践, SOP, 接入, 新增站点, 签到站, newapi, 公益站, ainovel,
  ai-novel, novel 部署/备份/生产, CPA, tebi, pxed, Bohrium, google-vps, novel.mangoq,
  ainovel.mangoq, 查文档, 查知识库, Obsidian, 运维文档, 部署手册, 备份仓, 记录文档,
  写笔记, 记录到obsidian, 更新文档, 记到知识库, 新建笔记, 整理文档, supervisord,
  cloudflared token, /personal/pxed, 或任何可能已有现成操作规范的技术运维与接入任务.
---

# Obsidian 文档路由与事前最佳实践规范（强制）

## Iron Law（三大核心铁律）

```
1. 事前（最佳实践铁律）：NO ACTION BEFORE BEST-PRACTICE LOOKUP
   执行任何接入、配置、开发、部署、升级或运维任务前，必须先查验知识库是否已有既定「最佳实践 / SOP / Canonical 规范」。有现成规范必须严格继承执行，严禁凭直觉重造轮子或做无用现场试错！

2. 读时（权威路由铁律）：NO OPS ANSWER FROM MEMORY OR BLIND SEARCH UNTIL AI-DOC-ROUTER IS READ
   严禁凭记忆盲答或全库随意 grep 碎片；必须查阅 00.MOC/AI-DOC-ROUTER.md 并以下钻的 canonical 权威入口为准。

3. 写后（防孤岛闭环铁律）：NO ORPHAN DOC
   新建/修改文档必须闭环双向挂载回 AI-DOC-ROUTER 与 MOC 索引，严禁留孤儿笔记。
```

- **违反事前铁律** = 盲目重写已有逻辑、现场反复 live 踩坑、产生大量重复无用功，甚至破坏已有稳定生产环境。
- **违反读时铁律** = 用过期路径、废弃域名或陈旧拓扑行动的高概率生产事故。
- **违反写后铁律** = 辛苦记录的排查与结论沦为知识孤岛，后续会话永失引用。

---

## Vault 位置

```bash
# 多机同步，各机路径不同（带空格必须加双引号）
# macOS:
"$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/obsidian-note"
# Windows:
"E:/profile/note/note"
# 定位存疑时：能跑通 `python3 .local/bin/doc-lookup --list` 即说明 vault 找对了（脚本会回退 cwd）
```

权威路由表（相对 vault 根）：
```
00.MOC/AI-DOC-ROUTER.md
```

---

## 一、 事前查验最佳实践机制（Pre-flight Best-Practice Gate）

当用户给出任何操作类任务指令时（例如：**接入新签到站/API渠道、部署新组件、改写配置、升级版本、环境初始化等**），**严禁直接动手编码或盲目启动测试**。必须先经过以下 3 步门控：

### 1. 必查既有最佳实践与 SOP
在动手之前，执行检索（按优先级）：
- **方式 A（首选脚本）**：在 vault 根执行 `python3 .local/bin/doc-lookup "<领域/业务词> 最佳实践"` 或 `<关键词> SOP` / `<关键词>`。
- **方式 B（直查路由表）**：Read `00.MOC/AI-DOC-ROUTER.md` 中对应的业务板块，直奔其「速查」列与「权威入口」。
- **方式 C（检查经验目录）**：检查 `Note/AI/经验/` 或 `Note/Infra/` 下是否存在对应主题的成熟手册（如《公益站签到运维手册》、《tebi CPA 栈部署与运维》等）。

### 2. 严格继承，杜绝无用功（Zero Redundant Work）
- **有现成标准化模式的，直接配置化接入**：
  - *典型示例*：标准 New API 站点接入，知识库明确规定通过声明式配置加入 `sites.yaml` 与相关资产清单即可，**绝不要**重新编写一套专用爬虫脚本，**更不要**为了验证去执行多余的 live 浏览器自动化测试（CDP 撞验证码/邀请码）。
  - *典型示例*：服务升级有成熟的「影子实例法 SOP」，必须严格遵循端口分配与平滑割接步骤，不得随心所欲现场测试。
- **禁止自行发明新变体**：除非现有最佳实践被验证已过时失效，否则必须 100% 沿用库内验证过的技术选型、路径规范与命令标准。

### 3. 未命中最佳实践时的处理
- 若检索确认知识库尚无该任务的最佳实践：
  1. 遵守通用工程约束与最小改动原则；
  2. 若改动涉及生产架构或未来可复用流程，在任务完成后执行**「写文档防丢 SOP」**，就地提炼为新的最佳实践沉淀进库。

---

## 二、 读与查询流程（答复与下钻）

1. **查路由**：
   - 方式 A：在 vault 根执行 `python3 .local/bin/doc-lookup "<query>"`（查询按空白分词、全部分词命中才算命中，范围含速查列）。
   - 方式 B：**Read** `00.MOC/AI-DOC-ROUTER.md` 整篇。
2. **读入口**：用用户触发词匹配表中「权威入口」→ **Read 入口整篇**。
3. **查细节**：需要深入再读入口链接的主手册；**禁止**用全库 `rg` 的任意碎片命中覆盖入口。
4. **冲突仲裁**：若入口与其它笔记冲突：**以入口 + 其指向的主手册为准**，并点名冲突文件。
5. **归因输出**：回答生产事实时写明依据笔记名（如「据 [[公益站签到运维手册]]」）。

### 路由未命中 Fallback 策略
若 `AI-DOC-ROUTER.md` 未命中：
1. 检查 `00.MOC/` 目录下相关索引（如 `技术笔记索引.md`、`项目索引.md`）。
2. 若仅在非 Canonical/历史排查笔记中搜到片段，**必须向用户声明**：「此信息仅在非权威历史笔记 [[xxx]] 中提及，生产可能已变更，建议核验」。
3. 协助用户将确认后的事实**就地登记**进 `AI-DOC-ROUTER.md`。

---

## 三、 Agent 记录文档防丢 SOP（写文档闭环）

Agent 新写文档沦为孤岛的根本原因是：**散落子目录、无标准元数据、未挂载进 MOC、未登记路由**。
每次为用户创建、重构或补充运维/技术/最佳实践文档时，**必须执行以下 5 步闭环**：

### 1. 规范落盘路径与命名
- 严禁随意堆在根目录。
- **经验 / 成熟 SOP / 最佳实践**：`Note/AI/经验/<主题>最佳实践.md`
- **运维 / 基础设施 / 部署手册**：`Note/Infra/<服务名或架构名>.md`（如 `Note/Infra/pxed 挂机脚本运维手册.md`）
- **项目开发文档**：`Note/Project/<项目名>/<项目名> 开发文档.md`
- **账号 / 资产清单**：`Note/Accounts/`（私有敏感；Agent 只登记结构与路径，不回显敏感密钥）
- 严禁落盘到 `01.项目/`、`02.技术/` 等库内不存在的历史别名目录。

### 2. 标准 Frontmatter 元数据
新建文档头部必须包含：
```yaml
---
title: <文档标题>
tags:
  - <主分类，如 Infra/Deploy/Ops/BestPractice>
  - <服务或领域名>
  - canonical  # 若为权威主手册/最佳实践
status: canonical # 或 active / draft
updated: YYYY-MM-DD
aliases:
  - <别名1>
  - <缩写>
---
```

### 3. 文档主体标准骨架
不要只写长篇过程流水账，前置提炼真相：
```markdown
# <文档标题>

## 速读（当前有效 · 维护于 YYYY-MM-DD）

- 一行生产真相 / 核心结论：当前运行机器、端口、关键规范、标准化操作步骤。
- 注意：此标题写法是 doc-lookup 速读区与 scan-stale-docs --strict-tldr 的解析契约，勿改成别的格式。

## 核心拓扑与规范 / 最佳实践原则
- **核心原则**：...
- **标准化模式**：...

## 标准操作 / 接入 / 部署 SOP
1. 第一步：...
2. 第二步：...

## 变更与排障记录
- YYYY-MM-DD: ...
```

### 4. 双向挂载（核心防丢防孤岛步骤）
新建文档或修改架构后，**必须在同一个任务内完成双向挂载**：
1. **登记路由**：在 `00.MOC/AI-DOC-ROUTER.md` 的表格中追加或更新对应的一行：
   - 领域 / 模块名
   - 触发词（只留高区分度关键词：服务名/操作动词/核心概念，≤15 个；doc-lookup 按空白分词全命中匹配，**禁止堆同义短语、版本号枚举**）
   - 权威入口（`[[笔记名]]`）
   - 主手册 / 下钻要点（速查列 ≤200 字；变更流水/修复链写进 canonical 手册，**不进路由表**）
2. **挂入主题 MOC**：在 `00.MOC/` 下对应的 `项目索引.md` / `技术笔记索引.md` 挂入双链链接。
3. **原地更新原则**：若已有对应主题的 Canonical 文档，**严禁另起新孤儿文件写流水账**，应在原 Canonical 文档相应段落就地追加更新，并修改文档头部的 `updated` 日期。

### 5. 校验闭环
在 vault 根执行健康检查：
```bash
python3 .local/bin/scan-stale-docs
```
确保无断链、无语法解析错误。

---

## 四、 核心反模式（严厉禁止）

- 🔴 **不做任何检索，直接凭空臆造操作方案**：接单后立刻开始写脚本、开浏览器打桩，把现存成熟 SOP 当空气。
- 🔴 **过度无用 live testing**：已有声明式配置或明确规范时，偏要启动 live 真实运行来验证（如多余的浏览器登录注册、撞验证码），浪费用户额度与时间。
- 🔴 **先 `rg` 随意读第一篇排查记录当真理**：把过期的历史调试片段当成当前的生产标准。
- 🔴 **凭过往会话模糊记忆直接修改机器或生产库**。
- 🔴 **只更新细节实现，不维护 Canonical 入口与路由表**。
- 🔴 **新写了 SOP/笔记后直接关闭会话，不挂载 MOC、不登路由表**（导致知识资产永久丢失）。
- 🔴 **稍有改动就建带时间戳的新文件**（如 `xxx-20261104.md`），使库内充满垃圾碎片。
- 🔴 **往 AI-DOC-ROUTER 堆同义触发词/版本号枚举，或把速查列当流水账**（破坏 lookup 性能与纯度）。

---

## 五、 与其它 skill 的关系与前置优先级

- **前置优先级第一**：当涉及 coding、debugging、ops、deploy、browser-use 等任何具体执行类 skill 时，**本 skill 的「事前查验最佳实践铁律」具有最高前置优先级**。在开始写代码或启动自动化测试前，必须先行调用本 skill 完成知识库 SOP 查验。
- **边界明确**：本 skill 负责 **「行动前查验最佳实践」**、**「读哪篇权威文档」** 与 **「产出如何防丢沉淀」**；具体的实现与调试动作由相应专业 skill 完成，但该动作必须在既有最佳实践指导下进行。
