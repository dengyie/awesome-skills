# Windows Provider

在目标 Windows 上以管理员执行。把占位符换成操作者现场提供的值，不要把替换后的文件提交到仓库。

## OpenSSH

先试系统能力包：

```powershell
$cap = Get-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
if ($cap.State -ne "Installed") {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
}
```

`0x80240438` 表示 Windows Update 端点失败，云电脑上常见。改用微软发布的 Win32-OpenSSH 便携版，运行其 `install-sshd.ps1`，得到原生 `sshd` 服务即可。

先看 sshd 现在听哪里。已有非环回入口时，不要改配置、不要重启，否则原来的管理 SSH 会断。只有确认可以收紧时，才追加环回地址：

```powershell
$cfg = "$env:ProgramData\ssh\sshd_config"
$listening = @(Select-String -Path $cfg -Pattern "^\s*ListenAddress\s+(\S+)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value })
$public = @($listening | Where-Object { $_ -notin @("127.0.0.1", "::1") })
if ($public.Count -gt 0) {
    throw "sshd already listens on $($public -join ', '); refusing to change it"
}
if ($listening -notcontains "127.0.0.1") {
    Add-Content -Path $cfg -Value "ListenAddress 127.0.0.1" -Encoding ascii
}
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell `
    -Value "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -PropertyType String -Force | Out-Null
Restart-Service sshd
Set-Service sshd -StartupType Automatic
```

不要新建入站防火墙规则。STCP 下 22 不面对公网。

## frpc.toml

文件必须是 UTF-8 **无 BOM**。PowerShell 5.1 的 `Set-Content -Encoding UTF8` 会写 BOM，frpc 0.71.0 会报 `invalid character at start of key: ï`。用下面的写法：

```powershell
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("C:\frp\frpc.toml", $content, $utf8)
```

内容：

```toml
serverAddr = "<FRPS_ADDR>"
serverPort = <FRPS_PORT>
auth.method = "token"
auth.token = "<FRPS_TOKEN>"
# 仅当 frps.toml 有 transport.tls.force = true 时保留下一行，否则删除
transport.tls.enable = true
loginFailExit = false

log.to = "C:\\frp\\frpc.log"
log.level = "info"
log.maxDays = 3

[[proxies]]
name = "<PROXY_NAME>"
type = "stcp"
secretKey = "<STCP_SECRET>"
localIP = "127.0.0.1"
localPort = 22
```

`log.to` 由 frpc 自己写和轮转。启动脚本不要再 `>> frpc.log`，否则重连会把磁盘写满。

二进制用与 frps 相同的版本，例如 `frp_<版本>_windows_amd64.zip` 里的 `frpc.exe`，放到 `C:\frp\frpc.exe`。GitHub 直连慢时换操作者自己的镜像，不要在脚本里写死某个人的下载站。

## 常驻

优先用 NSSM 服务。进程被强制结束、崩溃或正常退出时，它都会拉起，不依赖任务状态：

```powershell
C:\frp\nssm.exe install FRPWinSsh C:\frp\frpc.exe
C:\frp\nssm.exe set FRPWinSsh AppDirectory C:\frp
C:\frp\nssm.exe set FRPWinSsh AppParameters "-c C:\frp\frpc.toml"
C:\frp\nssm.exe set FRPWinSsh AppExit Default Restart
C:\frp\nssm.exe set FRPWinSsh AppRestartDelay 5000
C:\frp\nssm.exe set FRPWinSsh Start SERVICE_AUTO_START
C:\frp\nssm.exe start FRPWinSsh
```

经 SSH 调用 NSSM 时，反斜杠可能被外壳吃掉。写完后读 `HKLM\SYSTEM\CurrentControlSet\Services\FRPWinSsh\Parameters` 的 `Application` 和 `AppParameters`，确认仍是 `C:\frp\...`。读回错误就用 `Set-ItemProperty` 改这两项，再 `Start-Service`。

## 计划任务（没有 NSSM 时）

`Restart on failure` 只覆盖异常退出。frpc 被正常结束、或包装进程退出码为 0 时，任务会停在 Ready。所以除了开机触发，还要有周期触发。

这个兜底有明确边界：`IgnoreNew` 会跳过新启动。若 `frpc.exe` 已被强制结束或卡死，而任务仍显示 Running，每 5 分钟的触发不会再开一个进程。遇到这种情况，先结束任务实例再启动，或者改用上面的 NSSM。

```powershell
$action = New-ScheduledTaskAction -Execute "C:\frp\frpc.exe" -Argument "-c C:\frp\frpc.toml" -WorkingDirectory "C:\frp"
$atBoot = New-ScheduledTaskTrigger -AtStartup
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration ([TimeSpan]::MaxValue)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "FRP_WIN_SSH_Provider" -Action $action `
    -Trigger @($atBoot, $repeat) -Principal $principal -Settings $settings -Force
Start-ScheduledTask -TaskName "FRP_WIN_SSH_Provider"
```

直接运行 `frpc.exe`，不要套一层 `cmd /c`。`IgnoreNew` 只用于避免两个 frpc 同时运行，它不是进程被杀死后的恢复机制。

日志里出现 `start proxy success` 才算 Provider 就绪。

## 公钥

先确认账户属于哪个组。Administrators 组成员会被 `sshd_config` 里这条覆盖：

```text
Match Group administrators
    AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

所以管理员公钥写 `C:\ProgramData\ssh\administrators_authorized_keys`，普通用户才写 `C:\Users\<user>\.ssh\authorized_keys`。文件只放一行，OpenSSH 公钥格式，末尾一个换行。

管理员文件的 ACL 必须收紧，否则 sshd 静默拒绝：

```powershell
icacls.exe "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
```

最终 ACL 里不应再有 `Authenticated Users`。配置没改就不必重启 sshd；改了 `ListenAddress` 或 `AuthorizedKeysFile` 才重启。

## 完成后删除

保留 `frpc.exe`、`frpc.toml`、frpc 写的 `frpc.log`。删除安装时留下的 `*.ps1`、`*.zip`、解压目录和预检日志。这些文件经常含有刚写入的 token。
