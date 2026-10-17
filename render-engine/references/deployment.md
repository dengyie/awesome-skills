# Render-Engine 从零部署与配置参考手册 (0 到 1 指南)

## 一、平台规格与免费层政策

Render.com 提供的免费 Docker Web Service 适合轻量级 Web-Box 与边缘实验环境：

| 约束项 | 平台规格 / 限制 | 架构应对策略 |
| :--- | :--- | :--- |
| **免费额度** | 每个免费账号每月 750 小时免费实例时间 | 单个实例全月 24 小时运行刚好消耗 720~744 小时，完全免费 |
| **信用卡门槛** | **无需绑定信用卡**即可创建 Docker Web Service | 新手零风险，无误扣费顾虑 |
| **内存限制** | 512 MB 物理硬上限（超出立即触发 OOMKilled） | 选用 Alpine 3.20 极简系统，核心基座空载内存仅 20MB ~ 35MB |
| **CPU 配额** | 0.15 vCPU（受 Linux cgroup quota 约束） | 看门狗 5 秒周期轮询，各组件均为事件驱动，避免空转消耗 |
| **网络设备权限** | 容器无 `/dev/net/tun`，缺乏 `CAP_NET_ADMIN` | EasyTier 强制启用 `--no-tun --use-smoltcp` 用户态协议栈 |
| **入站端口约束** | 仅允许单个入站公网端口（`$PORT`，默认 10000） | 引入 Caddy 反向代理做 URL Path 单端口四路分流 |
| **自动休眠机制** | 连续 15 分钟无入站公网 HTTP 请求自动 Spindown | 暴露 `/health` 轻量探针，配合外部 Uptime Bot 定时保活 |

---

## 二、从零注册与代码准备

### 1. 引导用户注册 Render.com 账号
1. 访问注册入口：`https://dashboard.render.com/register`。
2. 推荐点击 **"Sign up with GitHub"**：
   - 授权 GitHub 登录后，Render 会自动关联用户的 GitHub 身份。
   - 后续选择部署代码库时，可直接列出用户自己的公开和私有仓库。

### 2. Fork 或导入代码仓库
- **核心仓库**：`https://github.com/dengyie/render-engine`
- **为什么推荐 Fork？**
  - Fork 到用户个人 GitHub 名下后，Render 可以自动监听用户仓库的 `main` 分支变动，后续如果用户修改配置或更新镜像，无需手动重新上传，代码 Push 即可自动触发 Render 持续集成与部署。

---

## 三、部署方式与配置矩阵

### 方式 1：Blueprint 一键部署（官方推荐，最省心）
在浏览器打开以下地址：
```text
https://render.com/deploy?repo=https://github.com/dengyie/render-engine
```
*(已 Fork 的用户可将末尾 repo 替换为个人仓库链接)*

平台将读取仓库内的 `render.yaml` 规格，自动填充服务名称、Dockerfile 路径、健康检查探针与环境变量骨架：
- 确认 **Plan** 显示为 `Free`；
- 选择机房 Region（如 `Oregon (US West)` 或 `Singapore`）；
- 点击 **"Apply"** 即可开始自动化部署。

### 方式 2：手动创建 Web Service
1. 登录 Render 控制台，点击 **New +** -> **Web Service**；
2. 选择 **"Build and deploy from a Git repository"**，找到已授权的 `render-engine`；
3. 关键表单项填写对照表：
   - **Name**：`render-engine`（自定义）
   - **Region**：`Oregon (US West)`（推荐）
   - **Branch**：`main`
   - **Runtime**：`Docker`
   - **Instance Type**：`Free`
   - **Health Check Path**：`/health`（**关键**：若未填写，Render 无法精确检测 Caddy 是否就绪）

---

## 四、环境变量配置矩阵 (Environment Variables)

### 1. 基础认证与访问控制（推荐按需配置）

| 变量名 | 默认值 / 机制 | 说明 |
| :--- | :--- | :--- |
| `PORT` | `10000` | Render 动态传入的公网监听端口 |
| `SSH_PASS` | 自动生成 18 位随机字符串 | OpenSSH 与 Web 终端默认密码，在部署日志打印 |
| `TTYD_USER` | `admin` | Web 终端 HTTP BasicAuth 用户名 |
| `TTYD_PASS` | 默认与 `SSH_PASS` 相同 | Web 终端 HTTP BasicAuth 密码 |
| `SSH_PUBKEY` | *(可选)* | 自动安装至 `/root/.ssh/authorized_keys` 的公钥 |

### 2. 虚拟网格与可选功能（按需渐进激活）

| 变量名 | 默认值 | 作用与激活规则 |
| :--- | :--- | :--- |
| `ENABLE_EASYTIER` | `false` | 设为 `true` 或配置 `ET_NAME` 激活 EasyTier 用户态节点 |
| `ET_NAME` | `render-mesh` | EasyTier 虚拟网名称 |
| `ET_SECRET` | 随机生成 | EasyTier 虚拟网通信密钥 |
| `ET_IP` | `10.144.144.90` | 容器在虚拟网内的保留 IP |
| `ET_PEERS` | *(可选)* | 外部 Hub 列表（逗号分隔，如 `tcp://hub1:11010,tcp://hub2:11010`） |
| `ENABLE_SINGBOX` | `false` | 设为 `true` 或配置 `SINGBOX_UUID` 激活 sing-box 混合代理 |
| `SINGBOX_UUID` | *(可选)* | VLESS 鉴权标识符，监听路径 `/vless-ws` |
| `KOMARI_TOKEN` | *(可选)* | MangoHub 探针认证凭据（需配合 `KOMARI_ENDPOINT` 激活） |
| `KOMARI_ENDPOINT`| *(可选)* | MangoHub 监控面板地址（如 `https://hub.example.com`） |
| `KOMARI_FORCE_DISK_TOTAL`| `5368709120` | 虚拟磁盘总容量（5 GiB），修正 OverlayFS 宿主机度量泄露 |

---

## 五、Blueprint 规格文件模板 (`render.yaml`)

```yaml
services:
  - type: web
    name: render-engine
    env: docker
    plan: free
    region: oregon
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
        generateValue: true # Set manually if joining an existing mesh; leave generateValue for new isolated mesh
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
      - key: ENABLE_KEEPALIVE
        value: "true" # 启用自主 Inbound HTTP 保活巡检，防止 15 分钟闲置休眠
      - key: KEEPALIVE_INTERVAL
        value: "300" # 拨测频率（秒，默认 300 秒 / 5 分钟）
```

---

## 六、构建日志分析与凭据确认

在部署过程中，打开控制台的 **Logs** 页面，确认以下关键标志：

1. **随机密码生成与凭据遮蔽输出**：
   - **自动随机密码**：若未显式指定 `SSH_PASS`，容器启动时会打印以下横幅，指导用户复制登录：
     ```text
     ========================================================
       Root/Web password set to: XXXXXXXXXXXXXXXXXX
     ========================================================
     ```
   - **用户自定义密码**：若用户显式注入了自定义 `SSH_PASS`，生产容器在就绪日志中自动实施凭据脱敏，仅输出 `Pass: [CONFIGURED]`，避免静态机密被平台共享日志明文泄露。

2. **进程拉起日志**：
   ```text
   Starting OpenSSH daemon...
   Starting Caddy multiplexer on port 10000...
   Starting ttyd web terminal with persistent tmux session...
   ```

3. **探针验证成功**：
   平台日志显示收到 `/health` 的 `HTTP 200` 响应，控制台顶部状态从 **"In progress"** 变为绿色的 **"Live"**。
