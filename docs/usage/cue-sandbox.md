# Cue Sandbox Access

Use `cue-sandbox` when a Cue cloud sandbox with no inbound public SSH must join EasyTier mango-mesh, stay reachable over `ssh mesh-cue`, keep an India reverse-SSH fallback, and run a Komari probe (optionally with overlay mining).

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- log in to Cue over EasyTier TUN (`ssh mesh-cue`) instead of a public port
- keep India `:2222` as reverse-SSH fallback only, not as the daily login host
- land EasyTier as kernel TUN (`no_tun = false`, `listeners = []`) rather than Muse VM `--no-tun` + SOCKS5
- install the Linux Komari agent with `ping_group_range` and, for mining nodes, keep Web SSH enabled

Avoid when the machine already has inbound public SSH (run sshd directly), when you only need a generic reverse tunnel with no mesh (use `muse-reverse-ssh`), or when the host is a NAT Windows box (use `windows-ssh-stcp`).

## How It Works

```text
operator  ssh mesh-cue  ──EasyTier──►  Cue ubuntu@overlay:22
                                        │
                                        ├ easytier-mango-mesh (TUN)
                                        ├ komari-agent → Komari hub
                                        └ miner → hub overlay :7019
                                        │
Cue ssh -R 0.0.0.0:2222:localhost:22 ─► India public:2222   ← fallback only
```

Cue dials the mesh and the reverse tunnel outbound. India never becomes the login account host. Overlay mining depends on EasyTier, not on India.

## What's Bundled

The skill is a runbook. Credentials stay with the operator and are never committed:

- `references/ssh.md` — two keypairs, `GatewayPorts clientspecified`, Cue sshd, SSH config snippets
- `references/easytier.md` — TUN template, unit name `easytier-mango-mesh.service`, peer placeholders
- `references/probe.md` — Hub loopback `admin:addClient`, ICMP, mining env triad, overlay pool

Live numbers (fingerprints, Hub addresses, snapshot tags) live in the operator's Obsidian vault, not in this package.

## Deploy

1. **EasyTier TUN first.** Copy the vault mesh template; do not hand-edit `network_secret`. Confirm Hub `easytier-cli peer` shows Cue `.81`.
2. **Access key on Cue only.** Install the operator pubkey on Cue `ubuntu`, write `Host mesh-cue` with `IdentitiesOnly yes`. Prove `ssh mesh-cue` before touching India.
3. **Tunnel key on Cue only.** Generate `~/.ssh/tunnel-key` on Cue; append its pubkey to India `azureuser`. Set VPS `GatewayPorts clientspecified` (not `yes`) and open TCP 2222.
4. **Probe.** Mint the token via Hub loopback `admin:addClient`, write `/etc/komari-agent.env` mode `600`, enable systemd, set `ping_group_range = 0 2147483647`.
5. **Mining (only if required).** Pool is overlay `<HUB_OVERLAY>:7019`, whitelist Cue overlay IP in `devices.json` `_static_ips`, keep `AGENT_DISABLE_WEB_SSH=false`, and do not reinstall a live miner.

## Safety Boundaries

- Never commit private keys, agent tokens, mesh secrets, or wallets. Paths and fingerprints only.
- Two keypairs: access key stays on the operator machine; tunnel key stays on Cue. Do not reuse `id_rsa`. Do not create `ubuntu` on India. Do not copy the access key to any VPS.
- Cue public-facing sshd keeps `PasswordAuthentication no`.
- GitHub `releases/latest` 404s on prerelease tags — pin a snapshot.
- Do not `journalctl` SRBMiner or run `SRBMiner --version` during troubleshooting.

## Related

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [`muse-reverse-ssh`](muse-reverse-ssh.md) — generic reverse SSH without mesh
- [`windows-ssh-stcp`](windows-ssh-stcp.md) — Windows NAT SSH over FRP STCP
