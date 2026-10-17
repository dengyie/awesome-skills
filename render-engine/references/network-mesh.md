# Render-Engine 虚拟网络网格规范 (EasyTier smoltcp)

## 一、为什么需要用户态网络栈 (smoltcp)

Render.com 免费 Docker 实例部署在多租户容器编排系统（AWS us-east Kubernetes）中，具有如下限制：
1. **无 root 硬件特权**：容器无法挂载 `/dev/net/tun` 虚拟网络字符设备。
2. **缺乏网络能力集**：容器缺乏 Linux 内核特权 `CAP_NET_ADMIN`。
3. **传统 VPN 失效**：直接运行 WireGuard、Tailscale（内核模式）或 EasyTier（默认 tun 模式）会因设备不存在报错退出。

### 解决方案：EasyTier 用户态栈模式
EasyTier 内置基于 Rust 实现的纯用户态 TCP/IP 协议栈（`smoltcp`）。
运行命令关键参数：
```bash
easytier-core \
    --no-tun \
    --use-smoltcp \
    --network-name "$ET_NAME" \
    --network-secret "$ET_SECRET" \
    --ipv4 "$ET_IP" \
    --peers "$PEER_ARGS"
```

在该模式下：
- 节点不在 Linux 内核创建 `tun0` 网卡，直接在用户态解析虚拟 IP 数据包。
- 采用白名单代理映射机制，将虚拟网内的 TCP 连接反向解包并转发至本地监听的真实端口。

---

## 二、白名单端口与路由拓扑

在 `render-engine` 中，`easytier-core` 白名单放行以下本地服务端口：

| 端口 | 协议 | 对应服务 | 作用 |
| :--- | :--- | :--- | :--- |
| `22` / `2222` | TCP | OpenSSH Server | 虚拟网内加密登录管理，免除公网端口暴露风险 |
| `10808` | TCP | sing-box 混合代理 | 为网格内其它跳板或客户端提供代理回落服务 |

### 网络拓扑模型
```
[受信任运维机 / pxed 跳板]
          │
          │ (EasyTier 加密虚拟网络 mango-mesh: 10.144.144.0/24)
          ▼
   [EasyTier Peer Hub] (腾讯广州 / Azure 香港)
          ▲
          │
   (出站 WebSocket / TCP 连接)
          │
[Render 容器 (render-engine)]
  └── IP: 10.144.144.90 (主机名 render-box)
        └── smoltcp 用户态转发:
              ├── 10.144.144.90:22   -> 127.0.0.1:22 (SSHD)
              └── 10.144.144.90:10808 -> 127.0.0.1:10808 (sing-box)
```

---

## 三、常用运维与排查指令

### 1. 动态 Peer 注入与连接管理
若容器启动后由于网络抖动未接入网格，或需要临时接入中继节点：

```bash
# 检查当前虚拟网内所有对等节点连接状态与延迟
easytier-cli peer

# 检查当前已建立的连接器 (Connector)
easytier-cli connector

# 动态添加新的 Hub 节点（注意：必须使用 connector add，不可使用 peer add）
easytier-cli connector add tcp://212.64.10.215:11010
easytier-cli connector add tcp://104.208.65.233:11010
```

### 2. 网格连通性与打洞测试
在跳板机（如 `pxed`）上检测连通性：
```bash
# 检测与容器虚拟 IP 的延迟与丢包
ping -c 3 10.144.144.90

# 测试 22 端口连通性
nc -zv -w 3 10.144.144.90 22

# 通过跳板机直连
ssh -o ProxyJump=pxed root@10.144.144.90
```
