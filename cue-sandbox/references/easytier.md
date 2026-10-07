# Cue EasyTier

Cue **有 `/dev/net/tun`**，走内核 TUN。不要抄 Muse VM / pxed / tebi 的 `no_tun=true` + SOCKS5。

## 配置

路径现网：`/home/ubuntu/easytier/config.toml`，二进制 `/home/ubuntu/.local/bin/easytier-core`。

```toml
instance_name = "cue"
hostname = "cue"
ipv4 = "10.144.144.81/24"
listeners = []
rpc_portal = "127.0.0.1:15888"

[network_identity]
network_name = "mango-mesh"
network_secret = "<从 EasyTier 手册模板抄，禁止手编或改大小写>"

[[peer]]
uri = "tcp://<TENCENT_HUB>:11010"

[[peer]]
uri = "tcp://<HK_HUB>:11010"

[flags]
default_protocol = "tcp"
no_tun = false
```

- `listeners = []`：Cue 无公网入站，不要学 aws/india 开 `0.0.0.0:11010`。
- 双 Peer 都写，跨境 TCP。密钥与全网同构，手抄一次就会 `network identity not match`。
- 虚拟 IP 静态 `.81`，禁止 DHCP。`.80` 是 muse-vm。

Hub 公网地址以 vault EasyTier 手册矩阵为准，不要凭记忆改。不要把 Hub 公网地址写进本 skill。

## 常驻

现网单元名是 **`easytier-mango-mesh.service`**（`User=root`，`Restart=always`），不是通用 `easytier.service`。不要为了对齐手册标准名而改名，除非用户明确要求迁移。

若主机用 `systemd-networkd`，给 tun0 配 `Unmanaged=yes`，避免 IP 被抢走。

## 验收

```bash
systemctl is-active easytier-mango-mesh
ip -4 addr show tun0
# 在 HK Hub:
easytier-cli peer   # 应见 cue 10.144.144.81 p2p tcp、0% loss
```

操作者本机：`ping -c 3 10.144.144.81` 通后再 `ssh mesh-cue`。

EasyTier 挂了 overlay 矿也会断。印度 2222 不是这条隧道的依赖。
