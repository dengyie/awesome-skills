---
name: render-engine
description: Render.com 免费 Docker Web Service 容器（render-engine / render-box）的标准运维与操作 SOP。用于用户提到 render-engine、render-box、Render 容器、Render 部署、Render 掉线、Render 终端、Render EasyTier、10.144.144.90、Render 防休眠/保活、Caddy 多路复用、ttyd+tmux 持久化会话，或要在 Render 免费容器上运行安全 Linux Web-Box 时。包含一键部署、零配置基座、按需激活（EasyTier smoltcp / sing-box / Komari）、探活诊断与 OverlayFS 虚假磁盘告警排查。
---

# Render-Engine 容器运维与管理 SOP

`render-engine` 是专为 Render.com Free Tier 设计的单容器 Web-Box 运行时环境。底层基于 Alpine Linux，在无 `CAP_NET_ADMIN` 和无 `/dev/net/tun` 的严苛受限环境（512MB RAM 上限）下，通过 Caddy 单端口多路复用、OpenSSH、基于 tmux 会话持久化的 ttyd Web 终端，提供零配置开箱即用的 Linux 环境；并支持 EasyTier（smoltcp 用户态网络栈）、sing-box 代理和 Komari 探针的按需渐进式激活。

本 Skill 为面向 AI Agent 与运维人员的**完全自包含操作规程**。

```text
                               Render Public Edge (Port 10000 / HTTPS)
                                                 │
                                    ┌────────────┴────────────┐
                                    │    Caddy Multiplexer    │
                                    └────────────┬────────────┘
                                                 │
       ┌──────────────────────┬──────────────────┴──────────────────┬──────────────────────┐
       ▼                      ▼                                     ▼                      ▼
Path: /health          Path: /shell/                         Path: /et (WS)         Path: /vless-ws
┌──────────────┐       ┌──────────────────────┐              ┌──────────────────┐   ┌──────────────────┐
│ Health probe │       │ Web terminal (ttyd)  │              │ EasyTier Mesh    │   │ sing-box VLESS   │
│ (200 OK)     │       │ Basic Authentication │              │ (Optional)       │   │ (Optional)       │
└──────────────┘       └──────────┬───────────┘              └────────┬─────────┘   └──────────────────┘
                                  │                                   │
                         [tmux session: main]               [smoltcp user-space]
                                  │                                   │
                      ┌───────────┴───────────┐            ┌──────────┴──────────┐
                      ▼                       ▼            ▼                     ▼
             State persistence        Mouse scroll /   OpenSSH (Port 22/2222) sing-box (Port 10808)
             across reconnects        50k history      (In-mesh direct SSH)   (In-mesh mixed proxy)
```

按需查阅参考手册，避免一次性全量加载：
- `references/deployment.md`：Render Blueprint（render.yaml）、环境变量矩阵与一键部署
- `references/network-mesh.md`：EasyTier smoltcp 用户态组网、Peer 连接与免密 SSH 直连
- `references/terminal-persistence.md`：ttyd+tmux 断线保活机制与 WebSocket 自动化交互协议
- `references/troubleshooting.md`：常见排错（OverlayFS 宿主度量泄露、掉线根因与看门狗熔断）

---

## 快速自检与决策树 (Decision Tree)

接手 `render-engine` 相关任务时，按以下顺序决策与行动：

1. **探测目标容器存活与健康**：
   - 请求 `https://<render-host>/health`：
     - 若返回 `200 OK` → 容器处于存活服务状态。
     - 若返回 `502 Bad Gateway` 或超时 → 容器处于休眠（Spindown）、正在构建部署或 Caddy 异常崩溃。
2. **判断身份认证与凭据**：
   - 生产环境默认账号为 `admin`。
   - 若用户未显式设置 `SSH_PASS` / `TTYD_PASS`，容器启动时在控制台日志中自动生成并打印 18 位随机强密码。
3. **定位掉线告警根因**：
   - 若用户报告“Render 掉线”或“节点离线”，优先检查是否为 **MangoHub/Komari 监控面板告警** 或 **EasyTier 虚拟网失联**，而非容器本身宕机。详细排查步骤见下文 [工作流 4]。

---

## 工作流 1：服务探活与健康巡检

执行以下命令快速诊断目标实例的四层/七层状态：

```bash
TARGET_URL="https://render-engine.onrender.com"

# 1. 存活探针探测
curl -s -i "${TARGET_URL}/health" | head -n 5

# 2. 根路径多路复用回落验证
curl -s "${TARGET_URL}/"

# 3. Web 终端认证端点与 Token 接口探测
curl -s -i "${TARGET_URL}/shell/" | grep -E "HTTP/|WWW-Authenticate|via"
```

正常输出特征：
- `/health` 返回 `HTTP/2 200`，Body 为 `OK`。
- `/` 返回 `render-engine is running. Access /shell/ for web terminal...`。
- 未带认证访问 `/shell/` 严格返回 `HTTP 401 Unauthorized` 并携带 `WWW-Authenticate: Basic realm="ttyd"`。

---

## 工作流 2：Web 终端交互与会话保持

目标实例集成了 `ttyd` + `tmux` 持久化体系，客户端断线或页面刷新不会丢失终端上下文。

### 1. 浏览器人工访问
- 打开 `https://<render-host>/shell/`
- 输入 HTTP BasicAuth 凭据（如 `admin` / 密码）
- 自动挂载进入 `tmux` 的 `main` 会话，内置支持：
  - 鼠标滚轮滑动浏览；
  - 50,000 行历史缓冲区（`history-limit 50000`）；
  - `--ping-interval 15` 心跳防 Cloudflare/ALB 60s 静默断连。

### 2. Agent 自动化脚本交互（WebSocket）
在无浏览器环境（如命令行 Agent）下，可通过 Python 建立带 BasicAuth 的 WebSocket 连接执行命令，见 `references/terminal-persistence.md`。

---

## 工作流 3：EasyTier 网格连接与直连 SSH

当目标容器配置了 `ET_NAME` 时，EasyTier 自动激活，运行在用户态 `smoltcp` 模式（无需 `/dev/net/tun`）。

### 1. 外部机器接入该网格
在操作者机器或跳板机上运行：
```bash
sudo easytier-core \
  --network-name "<ET_NAME>" \
  --network-secret "<ET_SECRET>" \
  --ipv4 "10.144.144.100" \
  --peers "wss://<render-host>/et"
```

### 2. 验证对等拓扑
```bash
easytier-cli peer
```
若看到 `10.144.144.90`（`render-box`），说明 Mesh 虚拟通道打通。

### 3. SSH 直连登录
容器通过 smoltcp 白名单放行 22 端口，可直接登录：
```bash
# 密码认证（若未注入公钥）
sshpass -p "<SSH_PASS>" ssh -o StrictHostKeyChecking=no root@10.144.144.90

# 密钥认证（若已注入 SSH_PUBKEY）
ssh -o StrictHostKeyChecking=no root@10.144.144.90
```

---

## 工作流 4：排查与修复“节点掉线”问题

当用户反馈“线上 render-engine 掉线了”，按以下 SOP 快速定位并解决：

### 核心真相：公网存活 vs 私有 Mesh/监控脱靶
1. **先查公网**：`curl -s https://<render-host>/health`。若返回 200，说明**容器本身运转完好**。
2. **根因归纳**：
   - 掉线通常是**监控探针（Komari）离线**或 **EasyTier 无法打通**。
   - **典型诱因**：开源版本剥离了所有私有硬编码（如私有 VPS 域名、私有 Hub IP、固定 Token）。若用户在 Render 控制台未显式配置对应的环境变量，容器重新部署后将遵循规范**保持可选模块休眠**，进而导致监控面板因收不到心跳产生离线告警。

### 修复步骤：
1. **持久化修复（强烈推荐）**：
   指导用户或通过 Render 控制台补齐环境变量：
   - `ET_PEERS`：填入核心 Hub（如 `tcp://hub1:11010,tcp://hub2:11010`）
   - `KOMARI_ENDPOINT`：填入监控服务端地址（如 `https://monitor.example.com`）
   - `KOMARI_TOKEN`：填入节点专属 Token
   保存后 Render 自动重新部署并持久化恢复。
2. **即时热修复（通过 Web Terminal）**：
   若无需等待重新构建，可直接在 Web Terminal（`/shell/`）中执行：
   ```bash
   # 1. 动态为 EasyTier 注入对等 Hub
   easytier-cli connector add tcp://<hub-ip>:11010

   # 2. 写入探针配置并后台拉起
   cat > /etc/komari-agent.env << EOF
   export AGENT_ENDPOINT="<YOUR_ENDPOINT>"
   export AGENT_TOKEN="<YOUR_TOKEN>"
   export AGENT_INCLUDE_MOUNTPOINTS="/"
   export AGENT_FORCE_DISK_TOTAL="5368709120"
   EOF
   nohup /usr/local/bin/komari-agent --prefer-cgroup-limits >/dev/null 2>&1 &
   ```

---

## 工作流 5：辟谣“386G 磁盘爆满 80%~91%”告警

在监控面板或终端执行 `df -h` 时，常见如下告警：
```text
Filesystem                Size      Used Available Use% Mounted on
overlay                 386.9G    315.9G     51.3G  86% /
```
**生产真相与定案原则**：
- Render 免费实例为 AWS Kubernetes 上的多租户 unprivileged 容器，无独立底层块设备。
- `statvfs("/")` 与 `df -h` 汇报的 386GB 盘已用 315GB 是**宿主机物理节点的共享 OverlayFS 泄露**，绝非当前容器的真实占用。
- 容器真实占用仅约 **190MB ~ 250MB**，剩余空间充裕且健康。
- **严禁**盲目执行磁盘清理、删除系统文件或重装镜像。
- 探针通过 `AGENT_FORCE_DISK_TOTAL="5368709120"`（5 GiB）将监控总容量虚拟化收敛，杜绝面板虚假误报。
