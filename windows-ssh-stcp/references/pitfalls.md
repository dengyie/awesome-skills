# 实机踩坑

这些都在 frpc/frps 0.71.0、Win32-OpenSSH 9.5、Windows PowerShell 5.1 上复现过。

## 1. 复用中继时被教程带偏

旧教程通常写「新装 frps，bindPort 7000，只配 token」。已有 frps 时这样做会多开一个暴露面，还会和现网版本不一致。

正确做法：读现有 `frps.toml`。沿用它的端口和 token。只有它写了 `transport.tls.force = true`，客户端才加 `transport.tls.enable = true`；没有这行就不要加。STCP 不需要放行新端口，也不要动 `allowPorts`。

## 2. frpc 拒绝 UTF-8 BOM

PowerShell 5.1 `Set-Content -Encoding UTF8` 会写 `EF BB BF`。frpc 0.71.0 解析第一行就失败：

```text
toml: line 1, column 1: toml: invalid character at start of key: ï
```

用 `UTF8Encoding($false)` 写文件。无 BOM 的同一份内容可以正常登录。

## 3. 系统 OpenSSH 装不上

`Add-WindowsCapability` 返回 `0x80240438` 是 Windows Update 源失败，不是命令写错。官方 Win32-OpenSSH 便携版安装成服务后，横幅是 `SSH-2.0-OpenSSH_for_Windows_9.5`，后续公钥和 `sshd_config` 行为与系统版一致。

## 4. 计划任务「失败才重启」等于没守护

frpc 正常退出时，任务上次结果是成功，`RestartCount` 不会触发。表现是 dashboard 里 proxy 变为 offline，visitor 日志是：

```text
custom listener for [<PROXY_NAME>] doesn't exist
```

优先改成 NSSM 服务，`AppExit Default Restart` 加 `AppRestartDelay 5000`，进程被强制结束后也会拉起。

没有 NSSM 时，才在开机触发器之外加每 5 分钟的重复触发，并设置 `MultipleInstances = IgnoreNew`。这个组合只处理任务已经回到 Ready 的情况。进程被强制结束或卡死、而任务仍显示 Running 时，新触发会被忽略，不会恢复。直接执行 `frpc.exe`，不要用 `cmd /c` 包一层。

## 5. 日志重定向把轮转绕开

`frpc.exe >> frpc.log` 只会追加。网络抖动时这个文件无限增长。日志应写在 toml 里：

```toml
log.to = "C:\\frp\\frpc.log"
log.maxDays = 3
```

启动命令不要再重定向。

## 6. 管理员公钥写进用户目录也不会生效

`Match Group administrators` 把管理员的 `AuthorizedKeysFile` 指到 `C:\ProgramData\ssh\administrators_authorized_keys`。写到 `C:\Users\Administrator\.ssh\authorized_keys` 看起来正确，登录仍是 `Permission denied`。

该文件还必须断继承。目录上继承下来的 `Authenticated Users:(RX)` 会让 sshd 忽略整份密钥，且不给明确原因。收紧后只留 `SYSTEM:(F)` 和 `Administrators:(F)`。

## 7. 端口通不等于登录通

visitor 成功只说明两个 frpc 都在线。接下来按这个顺序分界：

| 看到的结果 | 断点 |
|---|---|
| `connection refused` on 2222 | 控制机 visitor 没在听 |
| `custom listener doesn't exist` | Windows frpc 不在线，或 proxy 名不一致 |
| 读不到 SSH 横幅 | sshd 没听 127.0.0.1:22，或 secretKey 不一致 |
| `Permission denied (publickey,...)` | 链路已通，差公钥文件或 ACL |
| `whoami` 返回预期用户 | 完成 |

## 8. dashboard 命令

frps 0.71 的 STCP 状态在 `/api/proxy/stcp`。`/api/proxy` 和 `/api/client` 返回 404。密码行如果是 `webServer.password = "..."`，按字段切分时口令在第二列，不是第四列。

## 9. 安装残留

为了分步执行而落在 `C:\frp` 的 ps1、zip 和解压目录，经常含有 token。验收通过后删掉。运行只需要 `frpc.exe`、`frpc.toml` 和 frpc 自己的日志。
