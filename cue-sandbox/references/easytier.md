# Cue EasyTier

Cue **有 `/dev/net/tun`**，走内核 TUN。不要抄 Muse VM / pxed / tebi 的 `no_tun=true` + SOCKS5。

所需配置由操作者提供：`<MESH_SECRET>`、`<TENCENT_HUB>`、`<HK_HUB>`（两个 `host:11010`）。不要手编 secret，不要凭记忆改 Hub。

## 配置

路径：`/home/ubuntu/easytier/config.toml`，二进制优先 `/home/ubuntu/.local/bin/easytier-core`（没有再 `which easytier-core`）。

```toml
instance_name = "<CUE_INSTANCE_NAME>"
hostname = "<CUE_INSTANCE_NAME>"
ipv4 = "<CUE_OVERLAY>/24"
listeners = []
rpc_portal = "127.0.0.1:15888"

[network_identity]
network_name = "mango-mesh"
network_secret = "<从现网模板抄，禁止手编或改大小写>"

[[peer]]
uri = "tcp://<TENCENT_HUB>:11010"

[[peer]]
uri = "tcp://<HK_HUB>:11010"

[flags]
default_protocol = "tcp"
no_tun = false
```

- `instance_name` / `hostname`：首台默认 `cue`。第二台及更多沙盒必须使用唯一短名（如 `cue-2`），严禁网内重名。
- `ipv4`：静态虚拟 IP，禁止 DHCP。首台默认 `10.144.144.81`；第二台及后续沙盒必须向操作者索取唯一的 `.8x`（如 `10.144.144.82`），严禁 IP 碰撞导致网络争抢。
- `listeners = []`：Cue 无公网入站，不要开 `0.0.0.0:11010`。
- 双 Peer 都写，跨境 TCP。密钥与全网同构，手抄一次就会 `network identity not match`。

写入前：

```bash
install -d -m 755 /home/ubuntu/easytier
# 把上面的 toml 写到 config.toml；secret 由操作者在本机粘贴，不经聊天
chmod 600 /home/ubuntu/easytier/config.toml
```

二进制不在就按 EasyTier 官方 release 装 linux 对应 arch，钉具体版本，不要追 `latest` 除非操作者指定。装完确认：

```bash
test -x /home/ubuntu/.local/bin/easytier-core || test -n "$(command -v easytier-core)"
```

## 常驻

单元名 **`easytier-mango-mesh.service`**（`User=root`，`Restart=always`），不是通用 `easytier.service`。已有这个名字就沿用，不要为了对齐标准名而改名。

```ini
[Unit]
Description=EasyTier mango-mesh (cue)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/home/ubuntu/.local/bin/easytier-core -c /home/ubuntu/easytier/config.toml
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

`ExecStart` 路径以本机实际二进制为准。然后：

```bash
systemctl daemon-reload
systemctl enable --now easytier-mango-mesh
```

若主机用 `systemd-networkd`，给 tun0 配 `Unmanaged=yes`，避免 IP 被抢走。

## 验收

```bash
systemctl is-active easytier-mango-mesh
ip -4 addr show tun0
```

`tun0` 必须持有配置里的 overlay。有 Hub 操作权时再：

```bash
easytier-cli peer   # 应见本机 hostname + overlay、p2p tcp、0% loss
```

没有 Hub 操作权不算失败：把 Cue 侧 `tun0` + unit active 交给操作者，请他们在 Hub 上看 peer。

操作者本机：`ping -c 3 <CUE_OVERLAY>` 通后再 `ssh mesh-cue`。

EasyTier 挂了 overlay 矿也会断。印度 2222 不是这条隧道的依赖。
