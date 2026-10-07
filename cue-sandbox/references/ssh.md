# Cue SSH

## 日常 vs 兜底

```bash
ssh mesh-cue      # 首选 EasyTier
ssh cue           # 同上
ssh cue-tunnel    # 仅 mesh 挂了：印度公网:2222
```

本机 `~/.ssh/config`（活文件为准；快照在 vault `ssh-config`）：

```sshconfig
Host mesh-cue cue
  HostName 10.144.144.81
  User ubuntu
  IdentityFile ~/.ssh/cue-access-key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 30
  ServerAliveCountMax 3

Host cue-tunnel
  HostName <INDIA_PUBLIC_IP>
  Port 2222
  User ubuntu
  IdentityFile ~/.ssh/cue-access-key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

每条 Host 必须显式 `IdentityFile` + `IdentitiesOnly yes`。不要依赖默认 `id_rsa`。

`<CUE_OVERLAY>` 现网是 `10.144.144.81`（`.8x` 沙盒段，`.80` 是 muse-vm）。`<INDIA_PUBLIC_IP>` 以 vault `india-vps` 为准，不要凭记忆写进 skill。

## 两把钥

| 钥 | 私钥 | 公钥 | 用途 |
|---|---|---|---|
| 访问钥 | 只在操作者本机 `~/.ssh/cue-access-key`（0600） | 只 Cue `/home/ubuntu/.ssh/authorized_keys` | 人登录 Cue |
| 隧道钥 | 只 Cue `~/.ssh/tunnel-key` | 印度 `azureuser` authorized_keys | Cue 连出 `-R` |

访问钥现网指纹见 vault `ssh-credentials`（comment `cue-access-key-to-cue`）。隧道钥 comment 形如 `reverse-ssh-tunnel-to-<india-ip>`。

不要：

- 用本机 `id_rsa` 当隧道钥（那是登录印度 `azureuser` 的）
- 把访问公钥拷到印度或任何 VPS
- 在印度创建 `ubuntu` 去接 `cue-tunnel`（User 是 Cue 上的 ubuntu，经 GatewayPorts 反弹）
- 在聊天/文档/skill 粘贴私钥或 `.pub` 全文
- 等 Windows 才能搭 Cue→印度隧道；Mac 也不是必需端

Windows 要登 Cue：在 Windows 自己生成访问钥，公钥仍装 **Cue ubuntu**。

## 印度中继

- 生效值 `sshd -T | grep gatewayports` 必须是 `clientspecified`。drop-in 即可，不要改成 `yes`。
- 云防火墙放行 TCP 2222。
- 隧道没起来时 2222 能 SYN、无 SSH banner，这是正常的。
- 印度自己的登录仍是 `ssh in` / `azureuser`，和 Cue 访问钥无关。
- 印度挂了不影响 mesh、探针、overlay 矿路。

## Cue sshd

- 经 2222 暴露的公网面保持 `PasswordAuthentication no`。
- sshd 听 `0.0.0.0:22` 可以：没有公网入站，mesh 和反向隧道都打这条。

## 验收

```bash
ssh mesh-cue 'whoami; hostname; ip -4 addr show tun0'
```

应落到 `ubuntu`、Cue 本机 hostname、tun0 持有 `.81/24`。
