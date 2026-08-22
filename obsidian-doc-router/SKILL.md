---
name: obsidian-doc-router
description: >
  MANDATORY documentation router for the user's Obsidian vault and any ops/deploy/infra
  task, or ANY action involving reading, writing, creating, updating, or refactoring
  knowledge base notes in Obsidian.
  BEFORE answering ops questions from memory or grepping the vault, you MUST Read
  00.MOC/AI-DOC-ROUTER.md and open only the canonical entry it names.
  WHENEVER writing/creating/modifying Obsidian docs or notes, you MUST strictly follow
  the Anti-Orphan Recording SOP (frontmatter, path, summary, and two-way link mounting
  to AI-DOC-ROUTER and MOC).
  Triggers when: user mentions ainovel, ai-novel, novel 部署/备份/生产, CPA, tebi,
  pxed, Bohrium, google-vps, novel.mangoq, ainovel.mangoq, 查文档, 查知识库, Obsidian,
  运维文档, 部署手册, 备份仓, 记录文档, 写笔记, 记录到obsidian, 更新文档, 记到知识库,
  新建笔记, 整理文档, supervisord, cloudflared token, /personal/pxed.
---

# Obsidian 文档路由与记录规范（强制）

## Iron Law

```
1. 读：NO OPS ANSWER FROM MEMORY OR BLIND SEARCH UNTIL AI-DOC-ROUTER IS READ
2. 写：NO ORPHAN DOC — 新建/修改文档必须双向挂载回 AI-DOC-ROUTER 与 MOC 索引
```

违反读铁律 = 用过期路径/域名行动的高概率事故。  
违反写铁律 = Agent 自己写的文档后续自己再也搜不到/读不到（沦为孤岛）。

---

## Vault 位置

```bash
# 绝对路径（带空格必须加双引号）
"$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/obsidian-note"
```

权威路由表（相对 vault 根）：

```
00.MOC/AI-DOC-ROUTER.md
```

---

## 一、 读与查询流程（每次相关请求）

1. **查路由**：
   - 方式 A（首选脚本）：在 vault 根执行 `python3 .local/bin/doc-lookup "<query>"`
   - 方式 B（工具直接读取）：**Read** `00.MOC/AI-DOC-ROUTER.md` 整篇。
2. **读入口**：用用户触发词匹配表中「权威入口」→ **Read 入口整篇**。
3. **查细节**：需要深入再读入口链接的主手册；**禁止**用全库 `rg` 的任意命中覆盖入口。
4. **冲突仲裁**：若入口与其它笔记冲突：**以入口 + 其指向的主手册为准**，并点名冲突文件。
5. **归因输出**：回答生产事实时写明依据笔记名（如「据 [[ainovel 文档索引]]」）。

### 路由未命中 Fallback 策略
若 `AI-DOC-ROUTER.md` 未命中：
1. 检查 `00.MOC/` 目录下相关索引（如 `技术笔记索引.md`、`项目索引.md`）。
2. 若仅在非 Canonical/历史排查笔记中搜到片段，**必须向用户声明**：「此信息仅在非权威历史笔记 [[xxx]] 中提及，生产可能已变更，建议核验」。
3. 协助用户将确认后的事实**就地登记**进 `AI-DOC-ROUTER.md`。

---

## 二、 Agent 记录文档防丢 SOP（写文档闭环）

Agent 新写的文档经常「失联」的根本原因是：**散落子目录、无标准元数据、未挂载进 MOC、未登记路由**。  
每次为用户创建、重构或补充运维/技术文档时，**必须执行以下 5 步闭环**：

### 1. 规范落盘路径与命名
- 严禁随意堆在根目录。
- **运维/基础设施/部署**：`Note/Infra/<服务名或架构名>.md`（如 `Note/Infra/pxed 挂机脚本运维手册.md`）
- **项目/产品主索引**：`01.项目/<项目名>/<项目名> 文档索引.md`
- **通用技术/模块实践**：`02.技术/<领域>/<主题名>.md`

### 2. 标准 Frontmatter 元数据
新建文档头部必须包含：
```yaml
---
title: <文档标题>
tags:
  - <主分类，如 Infra/Deploy/Ops>
  - <服务名>
  - canonical  # 若为权威主手册
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

> **速读 / 生产真相**：一句话说明当前运行机器、端口、关键域名、运行方式（如 Docker / Supervisor）。

## 核心拓扑与配置
- **主机 / 环境**：...
- **部署目录**：`...`
- **常用运维命令**：...

## 详细配置 / 部署 SOP
...

## 变更与排障记录
- YYYY-MM-DD: ...
```

### 4. 双向挂载（核心防丢防孤岛步骤）
新建文档或修改架构后，**必须在同一个任务内完成双向挂载**：
1. **登记路由**：在 `00.MOC/AI-DOC-ROUTER.md` 的表格中追加或更新对应的一行：
   - 领域 / 模块名
   - 触发词（中英文别名、常见运维动作全量列入，方便下次 lookup）
   - 权威入口（`[[笔记名]]`）
   - 主手册 / 下钻要点
2. **挂入主题 MOC**：在 `00.MOC/` 下对应的 `项目索引.md` / `技术笔记索引.md` 挂入双链链接。
3. **原地更新原则**：若已有对应服务的 Canonical 文档，**严禁另起新孤儿文件写排查流水账**，应在原 Canonical 文档的排障/变更段落追加，并更新文档头部的 `updated` 日期。

### 5. 校验闭环
在 vault 根执行健康检查：
```bash
python3 .local/bin/scan-stale-docs
```
确保无断链、无语法解析错误。

---

## 当前易错（若与路由表冲突，以路由表为准）

| 项 | 正确倾向 |
|---|---|
| ai-novel 生产 | Bohrium **pxed** + `ainovel.mangoq.ccwu.cc` |
| 不是 | google-vps + `novel.mangoq.ccwu.cc` 当生产 |
| 数据 | `/personal/pxed/ai-novel` |
| 配置备份 | `dengyie/ai-novel-backup`（无 DB） |

---

## 反模式（禁止）

- 先 `rg novel` 再读第一篇排查笔记当部署手册  
- 凭上一次会话记忆直接 SSH 改机器  
- 把 CPA 备份当成 novel 备份  
- 只更新细节文、不改 canonical 入口  
- **新写了排查/部署笔记后直接关会话，既不挂 MOC 也不登记 AI-DOC-ROUTER（导致后续 Agent 永失引用）**  
- **稍微有改动就建一个带时间戳的临时新文件，导致库内充斥过时垃圾笔记**  

---

## 与其它 skill 的关系

- 本 skill 管 **「读哪篇文档」** 与 **「文档如何写入防丢」**；不替代 systematic-debugging / 写代码 skill。  
- 若 using-superpowers 也适用：先满足 skill 检查，其中涉及 vault 运维文档时 **必须包含本路由流程**。

