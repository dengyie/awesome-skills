# Freestyle Sandbox 动态任务决策矩阵

## 1. 资源算力底线与账本
用户账号每月免费额度已减半：
- **vCPU-hrs**：100 核·时
- **Memory-hrs**：200 GiB·时
- **Storage-hrs**：30,000 GiB·时（足够保留多台 32GB 磁盘休眠机器）
- **Data Transfer**：25 GB

---

## 2. 动态规格与策略决策表

| 任务类型 | 推荐 Tier / 镜像 | 单月可用上限 | 空闲超时配置 | 生命周期与后处理 |
|---|---|---|---|---|
| **轻量测试 / Python 脚本 / 短时 CLI 工具** | `sm` (`freestyle/ubuntu-sm`, 2C/4G) | ~50 小时 | `--idle-timeout-seconds 600` | 任务完成后立即 `freestyle vm pause` |
| **Docker 镜像构建 / C/Rust 编译 / 重型并发** | `std` (`freestyle/ubuntu`, 4C/8G) | ~25 小时 | `--idle-timeout-seconds 300` | 构建产物拉回本地后立即 `freestyle vm pause` |
| **临时 Web 联调 / Webhook 接收 / API Demo** | `sm` (`freestyle/ubuntu-sm`, 2C/4G) | ~50 小时 | `--idle-timeout-seconds 1800` | 自动配置 `*.style.dev` TLS 域名，测试通过后暂停 |
| **危险代码试跑 / 不信任脚本隔离** | `sm` (可选 `--ephemeral`) | 按需 | 默认 | 一次性任务直接删机或恢复快照 |
| **长时间交互式编码（VS Code / Cursor Remote）** | `sm` 或 `std` | 视专注度而定 | 开启自动休眠 | 建立专属 Golden Snapshot，避免重配环境 |

---

## 3. 动态检查三部曲

1. **查存量（避免重复开机）**：
   运行 `freestyle --output json vm list`。如果存在已匹配的 VM（如 `sandbox-sm` 或 `sandbox-std`）：
   - 若状态为 `paused`，调用 `freestyle vm start <slug>` 唤醒（耗时仅几秒）。
   - 若状态已为 `running`，直接复用。

2. **按需新建**：
   如果尚无对应规格的沙箱，根据上述决策表选择合适的 `snapshot-id` 创建，**严禁省略 `--idle-timeout-seconds`**。

3. **闭环收尾（核心铁律）**：
   任务完成后，无论是脚本自动执行还是交互完成，必须确保 VM 转入 `paused` 状态，严禁无故裸跑常驻。
