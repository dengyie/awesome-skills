---
name: cue-sandbox
description: Cue 沙盒的 SSH、EasyTier mango-mesh TUN、Komari 探针与 overlay 挖矿接入 SOP。用于用户提到 cue、mesh-cue、cue-tunnel、Cue 探针、Cue EasyTier、Cue reverse-ssh、10.144.144.81、easytire/easytier Cue、印度 2222 兜底，或要把无公网入站的 Cue 接到 mesh / Komari / 挖矿中枢时。日常走 mesh，不要把印度 VPS 当登录机。
---

# Cue 沙盒接入（SSH / EasyTier / 探针）

Cue 没有公网入站。日常登录走 EasyTier TUN。印度 VPS 只反弹 SSH 兜底。探针跑在 Cue 本机。挖矿走 Hub overlay 口，不走公网 7019。

```text
操作者  ssh mesh-cue  ──EasyTier──►  Cue ubuntu@<CUE_OVERLAY>:22
                                      │
                                      ├ easytier-mango-mesh (TUN .81)
                                      ├ komari-agent → <KOMARI_ENDPOINT>
                                      └ srb-xel → <HUB_OVERLAY>:7019
                                      │
Cue ssh -R 0.0.0.0:2222:localhost:22 ─► 印度 azureuser@公网:2222   ← 仅兜底
```

本 skill **不含**私钥、agent token、mesh secret、钱包。真实值只在操作者本机密钥和 Cue `/etc/komari-agent.env`。现网数字以 Obsidian canonical 为准，先 `doc-lookup` 再动手。

深度细节按需读：

- `references/ssh.md`：两把钥、GatewayPorts、sshd、SSH config
- `references/easytier.md`：TUN 模板、systemd 单元名、验收
- `references/probe.md`：token 签发、ICMP、挖矿三件套、overlay 矿池

活事实挂在 vault（从 vault 根跑 `python3 .local/bin/doc-lookup "cue"`）：

- Cue 沙盒接入最佳实践 — 三件套入口
- EasyTier 全网虚拟网格组网运维手册 — 全网矩阵
- india-vps — 反向隧道中继
- Komari 探针后台运行最佳实践 — Linux systemd + ping_group_range
- Beszel-Komari 监控迁移计划 §20 — Cue 上线记录
- ssh-credentials / ssh-config — 别名与指纹

## 先决定，不要直接装

1. **日常入口是 mesh。** `ssh mesh-cue` 通了就不要改印度。印度挂了只断 `cue-tunnel`。
2. **Cue 有 TUN。** 不要抄 Muse VM / Bohrium 的 `--no-tun` + SOCKS5。
3. **两把钥。** 访问钥只在操作者本机，公钥只装 Cue `ubuntu`。隧道钥只在 Cue，公钥只装印度 `azureuser`。不要用 `id_rsa` 当隧道钥，不要在印度建 `ubuntu`，不要把访问钥放到任何 VPS。
4. **Mac 不是隧道的一端。** Cue 自己连出 `-R`。不要等 Windows，也不要为这条隧道改 Mac。
5. **挖矿已在跑就不要重装。** 排障不要 `journalctl` SRBMiner，不要 `SRBMiner --version`。

## 落地顺序

1. EasyTier TUN 起来，Hub `easytier-cli peer` 能看到 `.81`。
2. 访问钥装到 Cue `ubuntu`，本机写 `Host mesh-cue`。先 mesh 登录成功。
3. 隧道钥只在 Cue 生成；印度 `GatewayPorts clientspecified`（不要 `yes`）+ 云防火墙 2222。
4. 探针：Hub loopback `admin:addClient` 拿 token → `/etc/komari-agent.env` 600 → systemd → `ping_group_range`。
5. 若需要挖矿：池写成 overlay `<HUB_OVERLAY>:7019`，白名单 `_static_ips` 加 Cue overlay IP，探针带 miner URL + `{action}` 管控命令，且 **不要** `--disable-web-ssh`。

逐步命令见对应 `references/`。

## 铁律

- 私钥、token、secret、钱包不进仓库、文档、skill、聊天；只写路径和指纹。
- `GatewayPorts clientspecified`；Cue 公网面 `PasswordAuthentication no`。
- Komari token 只从 Hub 签发，不发明。API Key 是 admin 全权：只用在 Hub 必要节点，用完清临时文件。
- 挖矿节点禁止 `AGENT_DISABLE_WEB_SSH=true`。
- 白名单用 Hub `tcpdump` 和 `_static_ips`，不用 ipify，不改 `hub.env`。
- GitHub `releases/latest` 对 prerelease 404，二进制钉 snapshot 标签。
- 现网事实以 vault canonical 为准，禁止全库 rg 首个命中覆盖。

## 验收

- `ssh mesh-cue 'hostname; ip -4 addr show tun0'` 落到 Cue 且 tun0 持有 `.81/24`。
- Hub peer 列表有 `cue` p2p、0% loss。
- 探针日志 `Basic info uploaded` + `WebSocket connected`；Ping 任务 loss=0。
- 挖矿节点：`miner_configured` 与 `miner_controllable` 均为 true；`--pool` 是 overlay 不是公网 7019。
