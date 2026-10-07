# Cue SSH

在 Cue 本机或操作者本机都能做。没有 vault 时用操作者提供的公钥一行和 `<INDIA_PUBLIC_IP>`，不要停下来要 canonical。

## 日常 vs 兜底

```bash
ssh mesh-cue      # 首选 EasyTier
ssh cue           # 同上
ssh cue-tunnel    # 仅 mesh 挂了：印度公网:2222
```

操作者本机 `~/.ssh/config`：

```sshconfig
Host mesh-cue cue
  HostName <CUE_OVERLAY>
  User ubuntu
  IdentityFile ~/.ssh/cue-access-key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 30
  ServerAliveCountMax 3

Host cue-tunnel
  HostName <INDIA_PUBLIC_IP>
  Port <TUNNEL_REMOTE_PORT>
  User ubuntu
  IdentityFile ~/.ssh/cue-access-key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

每条 Host 必须显式 `IdentityFile` + `IdentitiesOnly yes`。不要依赖默认 `id_rsa`。

`<CUE_OVERLAY>` 首台默认 `10.144.144.81`（`.8x` 沙盒段，多台沙盒递增分配如 `.82`，严禁网内 IP 碰撞）。登录用户默认 `ubuntu`。`<INDIA_PUBLIC_IP>` 向操作者要一次。`<TUNNEL_REMOTE_PORT>` 首台默认 `2222`，多台沙盒接入同一中继时须递增分配（如 `2223`、`2224`），严禁远端端口争抢。

## 两把钥

| 钥 | 私钥 | 公钥 | 用途 |
|---|---|---|---|
| 访问钥 | 只在操作者本机 `~/.ssh/cue-access-key`（0600） | 只 Cue 登录用户 `authorized_keys` | 人登录 Cue |
| 隧道钥 | 只 Cue `~/.ssh/tunnel-key` | 印度 `<INDIA_USER>`（默认 `azureuser`）authorized_keys | Cue 连出 `-R` |

访问钥在操作者本机生成：

```bash
test -f ~/.ssh/cue-access-key || ssh-keygen -t ed25519 -f ~/.ssh/cue-access-key -C cue-access-key-to-cue -N ""
chmod 600 ~/.ssh/cue-access-key
```

把 **公钥一行** 交给 Cue（操作者自己贴到 Cue，或 agent 在 Cue 上写入）。不要把私钥发到聊天。

Cue 上安装访问公钥（以 `ubuntu` 为例）：

```bash
install -d -m 700 -o ubuntu -g ubuntu /home/ubuntu/.ssh
# 操作者把 cue-access-key.pub 的一行追加到 authorized_keys
chmod 600 /home/ubuntu/.ssh/authorized_keys
chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
```

隧道钥只在 Cue 生成（不要用操作者 `id_rsa`）：

```bash
test -f ~/.ssh/tunnel-key || ssh-keygen -t ed25519 -f ~/.ssh/tunnel-key -C "reverse-ssh-tunnel-to-<INDIA_PUBLIC_IP>" -N ""
chmod 600 ~/.ssh/tunnel-key
cat ~/.ssh/tunnel-key.pub
```

公钥追加到印度 `<INDIA_USER>` 的 `authorized_keys`。私钥留在 Cue。

不要：

- 用本机 `id_rsa` 当隧道钥（那是登录印度的）
- 把访问公钥拷到印度或任何 VPS
- 在印度创建 `ubuntu` 去接 `cue-tunnel`（User 是 Cue 上的 ubuntu，经 GatewayPorts 反弹）
- 在聊天/文档/skill 粘贴私钥或 `.pub` 全文
- 等 Windows 才能搭 Cue→印度隧道；操作者笔记本也不是必需端

Windows 要登 Cue：在 Windows 自己生成访问钥，公钥仍装 **Cue 登录用户**。

## 印度中继（可选）

用户没要求兜底就整段跳过。

- 生效值 `sshd -T | grep gatewayports` 必须是 `clientspecified`。drop-in 即可，不要改成 `yes`。
- 云防火墙放行 TCP `<TUNNEL_REMOTE_PORT>`（首台默认 2222，多台递增）。
- **生产推荐**：在 Cue 上配置 systemd 常驻守护服务 `/etc/systemd/system/cue-reverse-tunnel.service`：

  ```ini
  [Unit]
  Description=Cue reverse SSH tunnel to India fallback
  After=network-online.target
  Wants=network-online.target

  [Service]
  Type=simple
  User=ubuntu
  ExecStart=/usr/bin/ssh -N -T \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o BatchMode=yes \
    -i /home/ubuntu/.ssh/tunnel-key \
    -R 0.0.0.0:<TUNNEL_REMOTE_PORT>:localhost:22 \
    <INDIA_USER>@<INDIA_PUBLIC_IP>
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target
  ```

  启用命令：`sudo systemctl daemon-reload && sudo systemctl enable --now cue-reverse-tunnel`。

- **仅临时排障验证**：单次后台拉起（机器重启或长连接中断后失效，不可替代 systemd）：

  ```bash
  ssh -N -f \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o BatchMode=yes \
    -i ~/.ssh/tunnel-key \
    -R 0.0.0.0:<TUNNEL_REMOTE_PORT>:localhost:22 \
    <INDIA_USER>@<INDIA_PUBLIC_IP>
  ```

- 隧道没起来时该端口能 SYN、无 SSH banner，这是正常的。
- 印度自己的登录仍是 `<INDIA_USER>`，和 Cue 访问钥无关。
- 印度挂了不影响 mesh、探针、overlay 矿路。

## Cue sshd

- 经 2222 暴露的公网面保持 `PasswordAuthentication no`。
- sshd 听 `0.0.0.0:22` 可以：没有公网入站，mesh 和反向隧道都打这条。

## 验收

操作者本机：

```bash
ssh mesh-cue 'whoami; hostname; ip -4 addr show tun0'
```

应落到 Cue 登录用户、本机 hostname、tun0 持有 overlay。没有操作者本机时，在 Cue 上确认 `authorized_keys` 已写入且 `sshd` 在听 22，把「请从你的笔记本执行 `ssh mesh-cue ...`」交给操作者。
