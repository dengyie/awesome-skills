# Cue Komari 探针与 overlay 矿

用户没提探针就整篇跳过。挖矿段再加一道门：用户没提挖矿就只做探针。

没有 vault 时向操作者一次要：`<KOMARI_ENDPOINT>`、Hub 上执行 `admin:addClient` 的方式（或已经写好的 token 文件路径）、可选的 snapshot 标签。token 不要发到聊天。

## token

1. 经 **Hub loopback** `POST http://127.0.0.1:<KOMARI_RPC_PORT>/api/rpc2` + API Key 调 `admin:addClient`。公网 `/api/rpc2` 会被 CDN/WAF 拦 403。
2. token 只写入 Cue `/etc/komari-agent.env`（root 600）。不发明、不进聊天/skill、不长期落盘到操作者本机。
3. API Key 是 admin 全权且可跳过 2FA：只用在 Hub，用完清临时文件。
4. 新节点走 addClient，不要从另一台机器抄旧 token。

没有 Hub shell 时：把「请在 Hub 上 addClient，把 token 写进 Cue `/etc/komari-agent.env`」交给操作者，Cue 侧继续准备二进制和 systemd。

## 二进制与服务

- 目录 `/opt/komari-agent`。优先用操作者指定的 fork / snapshot。
- GitHub `releases/latest` 对 prerelease **404**，钉 snapshot 标签。操作者没给标签就问一次，不要猜 `latest`。
- systemd：`User=root`，`Restart=always`，`RestartSec=5s`，`EnvironmentFile=/etc/komari-agent.env`。

```ini
[Unit]
Description=Komari agent
After=network-online.target

[Service]
Type=simple
User=root
EnvironmentFile=/etc/komari-agent.env
ExecStart=/opt/komari-agent/komari-agent
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## ICMP（必做）

Debian/Ubuntu 默认 `ping_group_range = 1 0` → 日志 `socket: permission denied`，面板 Ping 100% loss。

```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range = 0 2147483647" | sudo tee /etc/sysctl.d/99-custom.conf
sudo systemctl restart komari-agent
```

## env（探针最低集）

```bash
AGENT_ENDPOINT=<KOMARI_ENDPOINT>
AGENT_DISABLE_AUTO_UPDATE=true
AGENT_DISABLE_WEB_SSH=false
AGENT_MONTH_ROTATE=1
AGENT_INTERVAL=3
AGENT_INCLUDE_NICS=eth0
```

`AGENT_TOKEN=` 由操作者在本机写入，chmod 600。不要在聊天回显 env。

## env（仅挖矿节点再追加）

```bash
AGENT_MINER_API_URL=http://127.0.0.1:21554/api/v2/status
AGENT_MINER_CONTROL_CMD=systemctl {action} srb-xel
```

- `DISABLE_WEB_SSH=true` 会同时关掉 Web SSH **和** 挖矿管控。要让 `/admin/mining` 能管，就保持 false。
- `CONTROL_CMD` 必须含字面量 `{action}`。Cue 是 root systemd，不要抄带 `sudo` 的模板。
- `INTERVAL=10` 对 Hub `readWait=11s` 偏紧会 1006；Cue 用 3。
- 舰队保持 `--disable-auto-update`。不要为契约修复全舰队换二进制。

## overlay 矿池（默认不做）

已上线则不要重装。排障看 `/var/log/srb-xel.log`，不要 `journalctl -u srb-xel` 全文，不要 `SRBMiner-MULTI --version`。

- `--pool stratum+tcp://10.144.144.2:7019`（Hub overlay，`<HUB_OVERLAY>` 默认 `.2`）。
- 公网 `<HK_HUB>:7019` 从 Cue 会假握手、Hub `tcpdump` 0 包。不要把 Hub 公网 IP 写进 skill。
- 白名单：中枢 `devices.json` `_static_ips` 加 Cue overlay IP。不要写 `hub.env`。源 IP 用 Hub tcpdump 抓，不要信 ipify。
- mesh 私网 IP 不要注册成公网 knock；knock 凭证必须唯一。
- API 只留 loopback（默认 `21554`），INPUT 非 lo DROP。

## 验收

- 日志：`Basic info uploaded successfully` + `WebSocket connected using v2 protocol`。
- 没有 Hub 面板权限时：Cue 日志这两行就够，把「请在面板确认 Online / Ping loss=0」交给操作者。
- 挖矿：`miner_configured=true` 且 `miner_controllable=true`。
