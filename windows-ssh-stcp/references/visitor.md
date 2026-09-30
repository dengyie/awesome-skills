# 控制机 Visitor

visitor 与 Windows 使用同一个 frps 地址、端口、token，以及同一对 `<PROXY_NAME>` / `<STCP_SECRET>`。secretKey 不对时，端口能开，SSH 握手会失败。

```toml
serverAddr = "<FRPS_ADDR>"
serverPort = <FRPS_PORT>
auth.method = "token"
auth.token = "<FRPS_TOKEN>"
loginFailExit = false

[[visitors]]
name = "<PROXY_NAME>-visitor"
type = "stcp"
serverName = "<PROXY_NAME>"
secretKey = "<STCP_SECRET>"
bindAddr = "127.0.0.1"
bindPort = 2222
```

先确认 `127.0.0.1:2222` 没被占用。日志出现 `start visitor success` 后，用原始套接字读一行，期望：

```text
SSH-2.0-OpenSSH_for_Windows_<版本>
```

这一步只证明链路和 sshd，不证明公钥。

## SSH config

```sshconfig
Host win-ssh
    HostName 127.0.0.1
    Port 2222
    User <SSH_USER>
    IdentityFile ~/.ssh/<专用私钥>
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

密钥单独生成，不复用其他机器的私钥：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/<专用私钥> -C "<这台机器的备注>" -N ""
```

只把 `.pub` 的那一行交给 Windows 侧写入。私钥留在控制机。

## macOS 常驻

nohup 会在退出后留下一个死的 2222。用 LaunchAgent，`KeepAlive` 负责拉起，`ThrottleInterval` 防止连不上时打满 CPU。程序、配置和工作目录都必须是绝对路径，launchd 不会继承你的 shell 当前目录：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.win-ssh-visitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/绝对路径/frpc</string>
        <string>-c</string>
        <string>/绝对路径/frpc-visitor.toml</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/绝对路径</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>/Users/<you>/Library/Logs/win-ssh-visitor.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/<you>/Library/Logs/win-ssh-visitor.err</string>
</dict>
</plist>
```

加载前先卸掉同名旧实例，否则旧进程继续占着 2222，新进程启动失败：

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.local.win-ssh-visitor.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.local.win-ssh-visitor.plist
```

改 toml 后重复这两步。Linux 用 systemd user service，`Restart=always`，不要只在失败时重启。

## 验证

```bash
ssh win-ssh "whoami"
```

期望输出类似 `主机名\用户名`。同时在 Windows 上看 22 仍只有 `127.0.0.1`。
