# Render-Engine 部署与环境规范参考手册

## 一、平台运行时边界与资源配额

Render.com 免费 Docker Web Service 具备明确的底层环境约束：

| 约束项 | 平台规格 / 限制 | 架构应对策略 |
| :--- | :--- | :--- |
| **内存限制** | 512 MB 硬上限（超额直接 OOMKilled） | 选用 Alpine 3.20 极简基座，核心基座内存仅 20MB ~ 35MB |
| **CPU 配额** | 0.15 vCPU（受 cgroup quota 限制） | 进程休眠优化，看门狗 5s 周期轮询，无空转轮询 |
| **网络设备特权** | 无 `/dev/net/tun`，无 `CAP_NET_ADMIN` | EasyTier 强制启用 `--no-tun --use-smoltcp` 用户态栈 |
| **公网端口暴露** | 仅允许单个入站端口（`$PORT`，默认 10000） | 引入 Caddy 反向代理做 URL Path 单端口四路分流 |
| **自动休眠机制** | 连续 15 分钟无入站 HTTP 请求自动 Spindown | 暴露 `/health` 轻量探针，配合外部 Uptime Bot 定时保活 |

---

## 二、环境变量配置矩阵

### 1. 核心运行参数（默认零配置）

| 变量名 | 默认值 / 机制 | 说明 |
| :--- | :--- | :--- |
| `PORT` | `10000` | Render 动态传入的公网监听端口 |
| `SSH_PASS` | 自动生成 18 位随机字符串 | OpenSSH 与 Web 终端默认密码，在部署日志打印 |
| `TTYD_USER` | `admin` | Web 终端 HTTP BasicAuth 用户名 |
| `TTYD_PASS` | 默认与 `SSH_PASS` 相同 | Web 终端 HTTP BasicAuth 密码 |
| `SSH_PUBKEY` | *(可选)* | 自动安装至 `/root/.ssh/authorized_keys` 的公钥 |

### 2. 可选扩展模块（按需渐进式激活）

| 变量名 | 激活条件 | 功能与说明 |
| :--- | :--- | :--- |
| `ENABLE_EASYTIER` | 设为 `true` 或配置 `ET_NAME` | 启动 EasyTier 用户态虚拟网格节点 |
| `ET_NAME` | 声明虚拟网名称 | EasyTier 网络标识（默认 `render-mesh`） |
| `ET_SECRET` | 声明网格通信密钥 | EasyTier 网络通信秘钥 |
| `ET_IP` | 声明静态 IP | 容器在虚拟网内的 IP（默认 `10.144.144.90`） |
| `ET_PEERS` | 逗号分隔的外部 Hub 地址 | 主动连接的 Peer 列表（如 `tcp://hub1:11010,tcp://hub2:11010`） |
| `ENABLE_SINGBOX` | 设为 `true` 或配置 `SINGBOX_UUID` | 启动 sing-box 混合代理与 VLESS 入站 |
| `SINGBOX_UUID` | 声明 UUID 字符串 | VLESS 鉴权标识符，监听路径 `/vless-ws` |
| `KOMARI_TOKEN` | 声明 Token 且配置 `KOMARI_ENDPOINT` | 启动 MangoHub 探针并开始上报度量 |
| `KOMARI_ENDPOINT` | 必须显式声明 | 监控服务端地址（无此项则探针拒绝启动防泄漏） |
| `KOMARI_FORCE_DISK_TOTAL` | 默认 `5368709120`（5 GiB） | 虚拟磁盘总容量覆盖，修正 OverlayFS 虚假度量 |

---

## 三、Render Blueprint 一键部署规范 (`render.yaml`)

```yaml
services:
  - type: web
    name: render-engine
    env: docker
    plan: free
    region: oregon # 或 singapore / frankfurt
    dockerfilePath: Dockerfile
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: PORT
        value: 10000
      - key: SSH_PASS
        generateValue: true
      - key: TTYD_USER
        value: admin
      - key: TTYD_PASS
        generateValue: true
      - key: SSH_PUBKEY
        value: ""
      - key: ENABLE_EASYTIER
        value: ""
      - key: ET_NAME
        value: ""
      - key: ET_SECRET
        generateValue: true
      - key: ET_PEERS
        value: ""
      - key: ENABLE_SINGBOX
        value: ""
      - key: SINGBOX_UUID
        value: ""
      - key: KOMARI_TOKEN
        value: ""
      - key: KOMARI_ENDPOINT
        value: ""
```
