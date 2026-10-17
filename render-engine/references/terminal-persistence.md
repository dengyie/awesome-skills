# Render-Engine 终端持久化与 WebSocket 保活规范 (ttyd + tmux)

## 一、断联与上下文丢失根因分析

在基于云端容器（Render、K8s 等）运行公网 Web 终端（`ttyd`）时，常出现两大用户体验痛点：

### 1. 边缘网关空闲超时断开
- **传输路径**：用户浏览器 → Cloudflare CDN → AWS ALB / Envoy (Render Edge) → Caddy 反向代理 → `ttyd` 守护进程。
- **超时机制**：
  - Cloudflare 的 WebSocket 空闲超时阈值为 100 秒。
  - AWS ALB 与常见反向代理默认空闲超时为 60 秒。
- **现象**：当用户在终端停止按键输入超过 1 分钟，边缘网关未检测到 TCP/WebSocket 应用数据流，直接下发 TCP RST 或 FIN 包掐断连接。

### 2. 重连导致终端会话树被直接销毁
- **原生 ttyd 行为**：当浏览器接入 WebSocket 时，`ttyd` 默认 `fork()` 一个新的 `/bin/bash` 子进程。
- **SIGHUP 传播**：一旦网络波动导致 WebSocket 断开，`ttyd` 会立刻向其直属子进程发送 `SIGHUP` 信号。
- **后果**：会话中正在执行的长耗时任务、编译进程、未保存的环境变量全部夭折；用户重新刷新网页进入的是一个全新的空会话。

---

## 二、架构解决方案与落地规范

为彻底解决上述问题，`render-engine` 实施了“协议级心跳保活 + 进程级会话持久化”双层保障：

```
浏览器客户端 (Web Terminal)
       │
       │ WebSocket (带 HTTP BasicAuth, Base64 AuthToken 握手)
       ▼
   Caddy 边缘复用 (/shell/*)
       │ flush_interval -1 (无缓冲零延迟)
       ▼
  ttyd 守护进程 (--ping-interval 15, 每 15s 下发 Ping 帧阻断边缘掐断)
       │
       ▼
包装脚本 (/usr/local/bin/ttyd-session)
       │
       ▼
tmux Server (常驻守护 session: main)
       └── /bin/bash (上下文、前后台任务、环境变量持续驻留)
```

### 1. ttyd 应用层心跳与反向代理无缓冲
- **心跳保活**：启动参数显式追加 `--ping-interval 15`，每 15 秒主动向客户端发送 WebSocket Ping 帧，使整条链路上的中间件（ALB/Cloudflare）将长连接标记为 Active。
- **流式透传**：Caddyfile 对 `/shell*` 反向代理增加 `flush_interval -1`，确保数据包立收立转，无 TCP 缓冲区积压。

### 2. tmux 会话托管包装脚本 (`/usr/local/bin/ttyd-session`)
`ttyd` 不直接启动 `/bin/bash`，而是调用持久化包装脚本：
```bash
#!/bin/sh
exec tmux -f /root/.tmux.conf new-session -A -s main /bin/bash
```
- `-A` 参数（Attach or create）：如果 `main` 会话已存在，则无损直接接入；不存在则创建。
- `-s main`：全局唯一具名会话。
- **断线无损效果**：用户无论掉线多少次，`tmux` 始终在后台保持 `main` 会话运行。重新连入瞬间恢复上次退出的所有屏幕输出和输入状态。

### 3. 高度优化的终端配置 (`/root/.tmux.conf`)
- `set -g mouse on`：全面支持鼠标滚轮平滑回滚历史输出，点击切换面板。
- `set -g history-limit 50000`：保留 50,000 行终端回滚缓冲区。
- `setw -g aggressive-resize on` 与 `set -g window-size latest`：自动匹配最新接入客户端的视窗尺寸，避免多端连入时的字符错位或换行异常。
- `set -s escape-time 0`：消除 Vim/Bash 下按 Esc 键的 500ms 默认延迟。
- 暗黑极简状态栏：显示 `[main]` 会话名称与即时时间，视觉友好且不遮挡操作。

### 4. 优雅关机信号联动
容器在接收到 Render 平台的 `SIGTERM` 信号时，看门狗执行 `cleanup()`：
```bash
tmux kill-server 2>/dev/null || true
```
该操作会向 `tmux` 会话树下的所有后台进程发送有序退出信号，避免容器销毁瞬间被系统直接 `SIGKILL` 导致的文件未刷盘与数据损坏。
