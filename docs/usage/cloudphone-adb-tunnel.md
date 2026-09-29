# Cloudphone ADB Tunnel

Use `cloudphone-adb-tunnel` when a non-root Android cloud phone (or device) must be reachable from a computer over the internet for ADB and scrcpy, with no public port exposed on the phone and no root required.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- run `adb` / `scrcpy` against a cloud phone from anywhere through an encrypted relay
- deploy a self-healing frpc client inside Termux on a non-root Android device
- survive hostile Termux conditions: no `/tmp`, Go-binary DNS failures, broken curl, unconfigured apt mirrors
- harden Android 13+ so the tunnel survives the phantom process killer and battery doze

Avoid when the device is on the same LAN (plain `adb connect <ip>:5555` is simpler) or when you need browser/HTTPS access to the device rather than ADB.

## How It Works

```text
[desktop] adb client → frpc visitor (127.0.0.1:55556)
    → [VPS] frps blind relay (STCP, token + TLS, no ADB exposure)
    → [phone] frpc in Termux (STCP proxy → local adbd 127.0.0.1:5555)
```

The relay only ever sees encrypted frp traffic; the ADB port is never published. The phone side runs frpc under `termux-chroot` (proot) so the Go binary can read a resolv.conf — Android apps have no `/etc/resolv.conf`, and without this the Go resolver falls back to `[::1]:53` and dies with `connection refused`.

## What's Bundled

The skill is self-contained — credentials stay with the operator:

- `scripts/install-termux.sh` — sanitized Termux installer (interactive for the three connection secrets): visible dependency repair, chroot-based DNS for the Go binary, GitHub-first download chain with pinned sha256 and stall detection, 15 s self-healing keepalive.
- `scripts/spawn.sh` / `scripts/keepalive.sh` — the chroot spawn wrapper and dual-path (pgrep/ps) keepalive loop installed on the phone.
- `references/frps-setup.md` — VPS relay template (frps.toml, systemd, firewall, domain notes, v0.71 dashboard health checks).
- `references/pitfalls.md` — the full production pitfall runbook: missing `/tmp`, Go resolver `[::1]:53` fallback and the termux-chroot fix, curl symbol mismatch, silent pkg installs, heredoc paste collisions, phantom process killer, invisible port holders, Clash TUN fake handshakes, CDN cache purge discipline.

## Deploy

The skill ships the runbook; the operator keeps credentials and pre-filled scripts in a private local directory (never committed). End to end:

1. **Phone (Termux)**: paste-wrapped installer or one-line CDN download → writes frpc.toml, keepalive (15 s self-heal) and the chroot spawn wrapper → wait for `start proxy success`.
2. **Desktop**: start the frpc visitor → wait for `start visitor success` → `adb connect 127.0.0.1:55556`.
3. **Harden immediately** (`device_config put activity_manager max_phantom_processes 2147483647`, battery whitelist `+com.termux`, background/foreground appops) and verify each value by reading it back.
4. **Mirror**: `scrcpy -s 127.0.0.1:55556 --video-codec=h265 --video-bit-rate=2M` (keep bitrate ≤2M on a 3 Mbps relay).

## Pitfalls (all hit in production)

| Symptom | Root cause | Fix |
| --- | --- | --- |
| every download source "fails" | Termux has no root `/tmp`; curl cannot create the output file | scope all temp files to `$HOME/frp/tmp` |
| Go binary: `lookup … on [::1]:53: connection refused` | no `/etc/resolv.conf` for apps on Android; bionic-linked tools work fine | write nameservers to `$PREFIX/etc/resolv.conf`, launch frpc via `termux-chroot` |
| `CANNOT LINK EXECUTABLE "curl": cannot locate symbol "SSL_set_quic…"` | openssl/libcurl version mismatch | switch to Tsinghua mirror, `apt install -y openssl libcurl curl` |
| `pkg install` hangs silently | output swallowed + mirror unconfigured | install per-binary via `command -v` checks with visible output; auto-failover to a reachable mirror |
| long paste runs half-way then breaks | outer `cat << 'EOF'` collides with inner heredoc `EOF` | use a distinct wrapper delimiter (e.g. `INSTALL_EOF`) or the one-line CDN install |
| visitor `bind: address already in use` but nothing listens | root-owned invisible holder on 55555 | move visitor `bindPort` to 55556 |

Download chain order: GitHub official → mirror proxies → self-hosted CDN as last-resort fallback, with pinned sha256 verification and a 15 s stall detector that moves to the next source.

## Operational Notes

- The shareable installer must pass a no-secrets assertion (no token, secretKey, relay domain, or private IPv4) before publishing; publishing over the same CDN filename requires a Cloudflare cache purge (edge TTL is 1 day).
- After any tunnel change, update the private deploy kit README and the ops vault manual — the skill runbook points at them as the source of truth.

## Related

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
