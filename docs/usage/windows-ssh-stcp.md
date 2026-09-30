# Windows SSH over FRP STCP

Use `windows-ssh-stcp` when a Windows machine with no inbound public port — a Tianyi cloud PC, a cloud desktop, or an office box behind NAT — must be reachable by SSH, and an FRP server (`frps`) already exists.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- log in with `ssh` to a Windows host that cannot accept inbound connections
- reuse an existing `frps` instead of standing up a new one or opening port `7000`
- keep the Windows `sshd` on loopback only, with no public firewall rule for port `22`

Avoid when the machine is on the same LAN (plain SSH is simpler), when you need a browser or HTTPS endpoint rather than SSH, or when no `frps` exists yet and you would rather build one. For an Android cloud phone reached over ADB, use `cloudphone-adb-tunnel` instead.

## How It Works

```text
[control host] ssh client → frpc visitor (127.0.0.1:2222)
    → [existing VPS] frps blind relay (STCP, token + per-proxy secret)
    → [Windows] frpc outbound (STCP proxy → local sshd 127.0.0.1:22)
```

The Windows host only ever makes an outbound connection. `frps` never publishes port `22`, an STCP proxy consumes no `allowPorts` entry, and no new firewall rule is required. The visitor and the provider share one secret that is independent of every other proxy on the same server.

## What's Bundled

The skill is a runbook. Credentials stay with the operator and are never committed:

- `references/windows-provider.md` — OpenSSH install (capability package, with the official Win32-OpenSSH portable build as fallback), loopback-only `sshd`, the administrator authorized-keys file, a BOM-free `frpc.toml`, and NSSM as the preferred keepalive.
- `references/visitor.md` — the control-host visitor: macOS LaunchAgent with absolute paths, Linux systemd with `Restart=always`, and the SSH config snippet.
- `references/pitfalls.md` — production failures: UTF-8 BOM rejected by frpc, scheduled-task keepalive gaps, and the TLS line that must match the server.

## Deploy

1. **Windows**: install OpenSSH and bind it to `127.0.0.1:22` only. If a `ListenAddress` is already set to anything other than loopback, stop and refuse to change it.
2. **Windows**: write `frpc.toml` with `New-Object System.Text.UTF8Encoding $false`. PowerShell 5.1 `Set-Content -Encoding UTF8` writes a BOM, and frpc 0.71 rejects it.
3. **Windows**: keep frpc alive with NSSM (`AppExit Default Restart`). A scheduled task is the fallback, and it cannot recover a task stuck in `Running` after its process dies.
4. **Control host**: write the visitor bound to `127.0.0.1:2222`, with `loginFailExit = false`, and supervise it. On macOS the LaunchAgent needs absolute paths for the binary, the config, and `WorkingDirectory`.
5. **Verify**: read one line from `127.0.0.1:2222` and expect an SSH banner, then `ssh -p 2222`. On Windows, port `22` still shows only `127.0.0.1`.

## Operational Notes

- Add `transport.tls.enable = true` on the client only when the server config has `transport.tls.force = true`. On a server that does not force TLS, that line prevents the client from logging in.
- Match the frpc version to the running frps. A client built for a different major version will fail the handshake.
- Give this proxy its own `secretKey`. Reusing another proxy's secret couples their credentials.
- The shareable skill must contain no token, no STCP secret, no relay address, no account name, and no public-key body. Those live in the operator's private deploy kit.

## Related

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
