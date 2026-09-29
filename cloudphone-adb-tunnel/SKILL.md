---
name: cloudphone-adb-tunnel
description: Use when connecting a non-root Android cloud phone or device to a computer over the internet for ADB or scrcpy screen mirroring — deploying the Termux frpc tunnel (FRP STCP mode), running the VPS blind relay and desktop visitor, hardening against the Android 13 phantom process killer, or diagnosing Termux failures such as missing /tmp, Go binary DNS "[::1]:53 connection refused", curl OpenSSL symbol errors, silent pkg hangs, and long-paste truncation. Triggers: 云手机 adb, termux frp, scrcpy 投屏, adb 隧道打不通, adb offline, 幽灵进程.
---

# 云手机 ADB 公网隧道（FRP STCP）部署与排障

零信任远程 ADB：手机 Termux 内 frpc（stcp proxy → 设备 adbd 127.0.0.1:5555）→ VPS frps 盲中继（专用域名:48721）→ 电脑 frpc visitor → `adb connect 127.0.0.1:55556`。VPS 只转发加密流量，不暴露 ADB。

> 本 skill 的密钥与权威脚本在本机私有目录（见「生产真相」），不入库、不进任何分享物。

## 0. 先读生产真相，别凭记忆行动

- **密钥与权威脚本**：`~/project/cloudphone-frp/`（README 有生产真相、密钥表、全部命令；**目录含 token/secretKey，绝不入库、绝不写入任何分享物**）。
- **vault 权威手册**：`Note/Infra/云手机 ADB 中继运维手册.md`。改动了流程/脚本/端口后，按 obsidian-doc-router 规则回写手册与路由表。
- 修改 Termux 脚本时改 `phone/install-termux.sh`（自用预填），同步派生 `install-termux-share.sh`，跑无密钥断言后再发布到下载站。

## 1. 标准接入流程

### 手机端（新手机/重装 Termux）
两种给法，脚本幂等、失败重跑即可：
1. **自用**：把 `phone/install-termux.sh` 用 `cat << 'INSTALL_EOF' > ~/install-termux.sh` … `INSTALL_EOF` 包装整块粘贴 Termux，末尾接 `bash ~/install-termux.sh`。成功标志：`start proxy success`。
2. **分享**：`curl -fsSL https://<下载站>/pub/install-termux.sh -o ~/install-termux.sh && bash ~/install-termux.sh`，按提示输入三要素（服务器入口/token/secretKey，从自用脚本配置区或 README 密钥表取）。

### 电脑端（Mac）
```bash
cd ~/project/cloudphone-frp
nohup ./bin/frpc-macos-arm64 -c pc/frpc-visitor.toml > /tmp/frpc-visitor.log 2>&1 &
grep "start visitor success" /tmp/frpc-visitor.log
adb connect 127.0.0.1:55556 && adb devices   # 期望 device 状态
```

### ADB 通了立即做加固（防 Termux 被杀，否则 frpc/keepalive 活不长）
```bash
adb -s 127.0.0.1:55556 shell device_config set_sync_disabled_for_tests persistent
adb -s 127.0.0.1:55556 shell device_config put activity_manager max_phantom_processes 2147483647
adb -s 127.0.0.1:55556 shell dumpsys deviceidle whitelist +com.termux
adb -s 127.0.0.1:55556 shell cmd appops set com.termux RUN_IN_BACKGROUND allow
adb -s 127.0.0.1:55556 shell cmd appops set com.termux START_FOREGROUND allow
```
做完用 `device_config get`/`dumpsys`/`appops get` 逐项回读验证，不要只看命令不报错。

### 投屏
`scrcpy -s 127.0.0.1:55556 --video-codec=h265 --video-bit-rate=2M --max-size=1280 --max-fps=30`。VPS 出口仅 3Mbps，码率 ≤2M、卡顿降 1.5M。

## 2. Termux 硬坑（每条都实机踩过，按症状对号）

| 症状 | 根因 | 解法 |
|---|---|---|
| 脚本写 `/tmp/xxx` 后所有源下载全失败 | **Termux 无根目录 /tmp**（临时目录是 `$TMPDIR`=$PREFIX/tmp），curl 建不了输出文件 | 一律用 `~/frp/tmp` |
| Go 程序报 `lookup 域名 on [::1]:53: connection refused` | frpc 是 CGO 关闭的 Go 静态二进制，只认 `/etc/resolv.conf`；Android 应用没有此文件，Go 回退查环回 53 端口被拒。bionic 链接的 curl/apt 走 netd 不受影响——所以「curl 能用但 frpc 解析不了」 | 把 `nameserver 223.5.5.5 / 119.29.29.29` 写入 `$PREFIX/etc/resolv.conf`，并经 `termux-chroot`（proot 包）拉起 frpc——chroot 内 `/etc` 即 `$PREFIX/etc` |
| `CANNOT LINK EXECUTABLE "curl": cannot locate symbol "SSL_set_quic_tls_early_data_enabled"` | openssl 与 libcurl 版本错配（长期未升级的 Termux 常见） | 换清华源后 `apt install -y openssl libcurl curl`；安装脚本已内置自动修复 |
| `pkg install` 黑屏"没动静" | 输出被 `>/dev/null` 吞掉 + 软件源未配置/不通 | 依赖按 `command -v` 逐项检测、缺啥装啥、安装过程输出可见；默认源不通自动换清华镜像 |
| 粘贴长脚本回车没反应 / 跑一半崩 | 粘贴缓冲 + **heredoc 定界符撞车**：外层 `cat << 'EOF'` 会被脚本内 frpc.toml 的 `EOF` 提前截断 | 外层包装定界符用 `INSTALL_EOF`；或用 CDN 一行命令免粘贴 |
| 下载源全失败且分不清原因 | 墙/DNS 污染/文件写不了混在一起 | 固定 sha256 校验 + 单源 15s 均速 <1KB/s 判卡死换源。源链顺序：**GitHub 官方 → ghfast.top → ghproxy.net → gh-proxy.com → 自建下载站 CDN（兜底，最后才动用）** |

## 3. 电脑端与网络坑

- **visitor 端口用 55556，不是 55555**：实机上 55555 被一个 lsof/netstat 均不可见的 root 进程占住（裸 bind 报 Errno 48，adb 侧表现为「bind in use 与 connection refused 并存」）。换新电脑时 55555 可用则可改回。
- **Clash TUN 假握手**：TUN 会替目标完成 TCP 握手，`nc` 通 ≠ 真通；判定连通性必须看应用层数据（TLS 首字节、HTTP 状态码）或从外部主机实测。VPS IP 已加 Clash DIRECT 双写（订阅更新不丢）。
- adb 假死自愈：`adb disconnect 127.0.0.1:55556 && adb connect 127.0.0.1:55556`；还不行就两端重启 frpc（手机端 keepalive 15s 会自动拉起）。厂商客户端自己的本地中继（如 127.0.0.1:16384）与本隧道无关，offline 残留直接 disconnect。

## 4. 分发与发布纪律

- 分享版脚本**发布前必须跑断言**：不含 token、secretKey、frps 域名、私网 IPv4（127.0.0.1/公共 DNS 白名单除外）。自用版含密钥，绝不外发。
- 脚本发布到下载站 `/pub/` 后**必须 CF purge 该 URL**（/pub/ 有 24h 边缘缓存，同名覆盖不清缓存则对方拿到的还是旧版）；frpc 二进制升级用新版本号文件名可免 purge。
- 下载站 `/pub/` 走 CF 边缘缓存（zone cache rule，edge TTL 1d override_origin + 源站 nginx Cache-Control），边缘 HIT 比回源快数倍。

## 5. 排障速查

- **手机未注册**（脚本健康检查超时）：看 `~/frp/logs/frpc.log`（DNS/端口/token 错误）和 `~/frp/logs/keepalive.log`（chroot/解析失败会记在这）。
- **visitor 登录成功但 adb 连不上**：确认 listener 在 `lsof -nP -iTCP:55556 -sTCP:LISTEN`；frps 侧看 proxy 状态（dashboard 仅本机，走 SSH 隧道）。
- **全链路健康判据**：`adb devices` 显示 device；`adb shell getprop ro.build.version.release`；`adb shell "ps -A | grep -c [f]rpc"` ≥1。
