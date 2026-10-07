# Cue Komari 探针与 overlay 矿

通用三端 SOP 在 vault Komari 探针后台运行最佳实践。Cue 是 Linux VPS 那一套，外加挖矿三件套。

## token

1. 经 **Hub loopback** `POST http://127.0.0.1:<KOMARI_RPC_PORT>/api/rpc2` + API Key 调 `admin:addClient`。公网 `/api/rpc2` 会被 CDN/WAF 拦 403。
2. token 只写入 Cue `/etc/komari-agent.env`（root 600）。不发明、不进 vault/聊天/skill、不长期落盘到操作者本机。
3. API Key 是 admin 全权且可跳过 2FA：只用在 Hub，用完清临时文件。
4. 新节点走 addClient，不适用「空 hub 从源机读旧 token 插库」那条 SOP。

`<KOMARI_RPC_PORT>` 与 `<KOMARI_ENDPOINT>` 以 vault Komari / Cue SOP 为准。

## 二进制与服务

- 目录 `/opt/komari-agent`，fork `dengyie/mango-agent`。
- GitHub `releases/latest` 对 prerelease **404**，钉 snapshot 标签（现网标签以 Komari §20 为准）。
- systemd：`User=root`，`Restart=always`，`RestartSec=5s`，`EnvironmentFile=/etc/komari-agent.env`。

## ICMP（必做）

Debian/Ubuntu 默认 `ping_group_range = 1 0` → 日志 `socket: permission denied`，面板 Ping 100% loss。

```bash
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
echo "net.ipv4.ping_group_range = 0 2147483647" | sudo tee /etc/sysctl.d/99-custom.conf
sudo systemctl restart komari-agent
```

## env（挖矿节点）

```bash
AGENT_ENDPOINT=<KOMARI_ENDPOINT>
AGENT_DISABLE_AUTO_UPDATE=true
AGENT_DISABLE_WEB_SSH=false
AGENT_MONTH_ROTATE=1
AGENT_INTERVAL=3
AGENT_INCLUDE_NICS=eth0
AGENT_MINER_API_URL=http://127.0.0.1:21554/api/v2/status
AGENT_MINER_CONTROL_CMD=systemctl {action} srb-xel
```

- `DISABLE_WEB_SSH=true` 会同时关掉 Web SSH **和** 挖矿管控。要让 `/admin/mining` 能管，就保持 false。
- `CONTROL_CMD` 必须含字面量 `{action}`。Cue 是 root systemd，不要从 hermes 抄 `sudo`。
- `INTERVAL=10` 对 Hub `readWait=11s` 偏紧会 1006；Cue 用 3。
- 舰队保持 `--disable-auto-update`。不要为契约修复全舰队换二进制。

## overlay 矿池

已上线则不要重装。排障看 `/var/log/srb-xel.log`，不要 `journalctl -u srb-xel` 全文，不要 `SRBMiner-MULTI --version`。

- `--pool stratum+tcp://10.144.144.2:7019`（Hub overlay，`<HUB_OVERLAY>` 现网是 `.2`）。
- 公网 `<HK_HUB>:7019` 从 Cue 会假握手、Hub `tcpdump` 0 包。不要把 Hub 公网 IP 写进 skill。
- 白名单：中枢 `devices.json` `_static_ips` 加 `10.144.144.81`。不要写 `hub.env`。源 IP 用 Hub tcpdump 抓，不要信 ipify。
- mesh 私网 IP 不要注册成公网 knock；knock 凭证必须唯一。
- API 只留 loopback（Cue 现网 `21554`），INPUT 非 lo DROP。

## 验收

- 日志：`Basic info uploaded successfully` + `WebSocket connected using v2 protocol`。
- Hub：`online=true`；Ping 任务 1/2 `loss=0`。
- 挖矿：`miner_configured=true` 且 `miner_controllable=true`。
