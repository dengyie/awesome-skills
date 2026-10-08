---
name: freestyle-sandbox
description: >
  Freestyle.sh 云端 Linux 弹性沙箱/云开发机的动态检测、智能调度与生命周期管控 SOP。
  用于用户提到 freestyle、freestyle.sh、云开发机、Linux 沙箱、动态沙箱、云端编译、隔离跑脚本、或者要把任务放到 freestyle 云端执行时。
  核心逻辑：根据任务负载类型（轻量脚本/测试 vs 重型Docker构建/编译）动态选择 2核4G 或 4核8G 规格，开机前先检查存量并唤醒复用，强制配置空闲自动休眠，执行完毕立即暂停回收算力，严防免费算力额度超标。
---

# Freestyle Sandbox 动态调度与运维规范

Freestyle.sh 是专为开发与 AI 任务设计的超高速 Linux 虚拟机。由于用户账号为**减半的免费额度**（每月仅 100 vCPU-hrs、200 GiB-hrs，存储 30,000 GiB-hrs 充裕），**严禁将 VM 7×24 小时常驻运行**。

必须遵循**「动态选配、按需唤醒、用完即休眠」**原则。

---

## 核心决策矩阵（动态检测）

当接收到需要使用 Freestyle 沙箱的任务时，按以下四类动态判定：

```text
               ┌── 任务特征分析 ──┐
               │                 │
       [轻量日常/脚本测试]     [重型编译/容器构建]
               │                 │
      规格: 2核 4G (sm)        规格: 4核 8G (std)
     镜像: ubuntu-sm           镜像: ubuntu
     空闲超时: 600s            空闲超时: 300s
     月度预算: ~50 小时        月度预算: ~25 小时
```

1. **轻量任务（Tier: `sm`，默认首选）**：
   - 场景：Python 脚本执行、API 试调、轻量 CLI、文件转换、危险代码沙箱。
   - 镜像：`freestyle/ubuntu-sm`（2 vCPU / 4 GiB 内存 / 16 GB 磁盘）。
   - 默认 slug：`sandbox-sm`。

2. **重型任务（Tier: `std`）**：
   - 场景：Docker 镜像编译、C++/Rust/Go 重型打包、高并发压测、大模型数据预处理。
   - 镜像：`freestyle/ubuntu`（4 vCPU / 8 GiB 内存 / 32 GB 磁盘）。
   - 默认 slug：`sandbox-std`。

3. **外网暴露需求（Web 联调 / Webhook）**：
   - 绑定免配置的免费二级域名 `*.style.dev`，自动生成 HTTPS 证书：
     ```bash
     freestyle tls create --domain <name>.style.dev --from public --to vm=<slug>,port=<port>
     ```

---

## 执行三步法（自动化工作流）

### 步骤 1：状态与存量探测（绝不盲目新建）
在执行任何新任务前，先检查账号下的已有 VM：
```bash
freestyle --output json vm list
```
- 若已存在匹配规格的 VM（例如处于 `paused` 或 `stopped` 状态）：
  ```bash
  freestyle vm start <slug>
  ```
- 仅当不存在对应规格的 VM 时才新建，**必须显式声明空闲超时**：
  ```bash
  # 轻量机
  freestyle vm create --snapshot-id freestyle/ubuntu-sm --slug sandbox-sm --idle-timeout-seconds 600 --no-ssh
  # 重型机
  freestyle vm create --snapshot-id freestyle/ubuntu --slug sandbox-std --idle-timeout-seconds 300 --no-ssh
  ```

### 步骤 2：执行任务
- **快速执行单条/批量命令**：
  ```bash
  freestyle vm exec <slug> -- bash -c "<commands>"
  ```
- **文件上下行传输**：
  ```bash
  freestyle vm scp <local_path> <slug>:<remote_path>
  freestyle vm scp <slug>:<remote_path> <local_path>
  ```
- **交互式登录（向用户提供）**：
  ```bash
  freestyle vm ssh <slug>
  ```

### 步骤 3：收尾休眠（防额度耗尽铁律）
任务执行结束、产物已拉回本地后，**必须立即暂停虚拟机**：
```bash
freestyle vm pause <slug>
```
> **注意**：`pause` 状态会完整保留内存现场和磁盘数据，并且**完全停止扣除 CPU 与内存算力额度**。

---

## 快捷管理脚本

本 skill 自带了一键化包装脚本，位于：
`~/.agents/skills/freestyle-sandbox/scripts/manage.sh`

常用操作：
```bash
# 智能单次运行：自动唤醒/创建 -> 执行命令 -> 自动 pause 休眠
~/.agents/skills/freestyle-sandbox/scripts/manage.sh run sandbox-sm sm "python3 -c 'print(1+1)'"

# 确保实例存活
~/.agents/skills/freestyle-sandbox/scripts/manage.sh ensure sandbox-sm sm

# 手动休眠
~/.agents/skills/freestyle-sandbox/scripts/manage.sh pause sandbox-sm
```

---

## 铁律与红线
1. **绝不无超时裸开 VM**：创建任何 VM 必须包含 `--idle-timeout-seconds`。
2. **非交互式任务必须闭环 Pause**：跑批、跑构建完成后必须立即调用 `freestyle vm pause`。
3. **优先复用已有 VM**：严禁每执行一个小任务就新建一台然后再删除，重复拉镜像和重置环境会白白浪费 CPU 预热时间。
4. **轻量任务禁止越级开 4核**：默认一律使用 `sm` (2核4G)，把宝贵的 4核 时间留给大型 Docker / 编译任务。
