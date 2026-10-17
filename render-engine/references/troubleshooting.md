# Render-Engine 故障排查与诊断手册

## 一、排查总览与应急诊断入口

当遇到节点离线、服务无响应或资源告警时，请依序检查：
1. **轻量探针**：访问 `https://<service-name>.onrender.com/health`。若返回 HTTP 200 OK，说明底层容器网络与 Caddy 正常；若返回 502/503，说明 Render 正在冷启动或容器处于 CrashLoop。
2. **Web Terminal**：访问 `https://<service-name>.onrender.com/shell/`，使用配置的 `TTYD_USER` 与 `TTYD_PASS` 登入。
3. **看门狗与进程树检查**：
   ```bash
   ps aux
   ```
   核心进程应包含：`entrypoint.sh` (PID 1)、`caddy`、`/usr/sbin/sshd`、`ttyd`。若启用了扩展功能，还应包含 `easytier-core`、`sing-box`、`komari-agent`。

---

## 二、常见故障与处理方案

### 1. 虚假磁盘告警（OverlayFS 宿主机度量泄漏）

- **故障现象**：MangoHub (Komari) 探针或外部监控持续发出磁盘空间告警（如报告 `/` 已占用 315.9G / 386.9G，利用率高达 82%~91%）。
- **根因定性**：
  Render 免费 Web Service 部署在 AWS us-east Kubernetes 基础设施上。在无特权 Docker 容器中，`df -h` 与标准系统调用 `statvfs("/")` 会直接穿透容器隔离层，读取到 Kubernetes Worker 宿主机根磁盘的物理状态，而非容器内部自身的实际占用。
- **验证手段**：
  在终端中执行真实占用核验：
  ```bash
  du -sh / --exclude=/proc --exclude=/sys --exclude=/dev 2>/dev/null
  ```
  实际返回通常仅在 **190MB ~ 250MB** 左右，磁盘资源极为充裕健康。
- **解决方案**：
  无需在容器内删除任何文件。若使用 Komari 探针，通过配置环境变量进行容量归一化：
  ```bash
  AGENT_FORCE_DISK_TOTAL="5368709120" # 强制将监控卡片总容量设定为 5 GiB
  ```

---

### 2. 线上离线（节点在网格或监控面板中显示 Offline）

- **故障现象**：网格内 `10.144.144.90` 无法 ping 通，或 Komari 探针面板显示节点离线。
- **根因排查**：
  1. **Render 自动休眠（Spindown）**：
     - Render 免费 Web Service 在连续 15 分钟无入站公网 HTTP 请求时，会自动停止容器进入休眠。
     - **修复方式**：使用 UptimeRobot 或其他外部探活工具，每 5~10 分钟请求一次 `https://<service-name>.onrender.com/health` 维持容器活跃。
  2. **环境变量缺失**：
     - 若代码库重构清理了硬编码配置，但未在 Render 控制台注入 `ET_PEERS` 或 `KOMARI_ENDPOINT` / `KOMARI_TOKEN`，容器会降级为纯净基座模式，不会自动启动 EasyTier 或探针。
     - **修复方式**：登录 Render 控制台 -> Environment，补充对应变量并重新触发部署。
  3. **实时热恢复（无需重启容器）**：
     若临时通过 Web Shell 登入，可动态注入 Peer：
     ```bash
     easytier-cli connector add tcp://<hub-ip>:11010
     ```

---

### 3. Web 终端 BasicAuth 鉴权失败 (401 Unauthorized)

- **故障现象**：在浏览器输入密码后不断弹窗提示 401。
- **根因排查**：
  - 默认情况下，若未手动指定 `SSH_PASS`，容器在初次构建时会自动生成 18 位随机高强度密码。
  - 该密码会在启动日志的最前部打印：
    ```text
    ========================================================
      Root/Web password set to: XXXXXXXXXXXXXXXXXX
    ========================================================
    ```
- **修复方式**：
  - 在 Render 控制台的 "Logs" 查看初始化打印的随机密码。
  - 或者在 Render Environment 中显式配置固定密码：`SSH_PASS=YourSecurePass123!`，保存后服务会自动重启生效。

---

### 4. 看门狗日志分析与重启判定

`entrypoint.sh` 的看门狗循环每 5 秒监测一次子进程活跃度，并带有**连续崩溃熔断器**（最大允许连续失败 5 次）：

```bash
# 检查看门狗及服务日志输出
# 在容器内检查或通过 Render 控制台实时日志追踪：
tail -n 100 /var/log/messages 2>/dev/null || true
```

若某个子进程非正常退出，看门狗会尝试原地拉起；若其在拉起后立即再次退出且连续达到 5 次，容器将主动终止退出，以便触发 Render 平台的容器重建机制。
