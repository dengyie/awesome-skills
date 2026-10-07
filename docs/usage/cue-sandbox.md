# Cue Sandbox Access

Use `cue-sandbox` when a Cue cloud sandbox with no inbound public SSH must join EasyTier mango-mesh, stay reachable over `ssh mesh-cue`, keep an India reverse-SSH fallback, and optionally run a Komari probe (overlay mining only when the user asks).

The skill is completely self-contained and executable directly on the Cue host. All configurations are derived from local machine probing and operator-provided inputs. Probe the current machine, ask once for missing inputs, and continue setup without stopping for external documents.

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
                                        ├ easytier-mango-mesh (TUN: <instance_name>)
                                        ├ komari-agent → Komari hub
                                        └ miner → hub overlay :7019   ← only if requested
                                        │
Cue ssh -R 0.0.0.0:<port>:localhost:22 ─► India public:<port>   ← fallback only
```

Cue dials the mesh and the reverse tunnel outbound. India never becomes the login account host. Overlay mining depends on EasyTier, not on India.

## What's Bundled

The skill is a runbook. Credentials stay with the operator and are never committed:

- `references/ssh.md` — two keypairs, `GatewayPorts clientspecified`, Cue sshd, SSH config snippets, generate-and-install commands
- `references/easytier.md` — TUN template, unit `easytier-mango-mesh.service`, peer placeholders, systemd unit
- `references/probe.md` — Hub loopback `admin:addClient`, ICMP, optional mining env triad, overlay pool

Live numbers (fingerprints, Hub addresses, snapshot tags) come from the operator in one batch.

## Deploy

1. **Probe the current machine.** Decide Cue vs operator laptop from `tun0` / `ubuntu` / `cue-access-key`. Do not stop to request external documentation.
2. **Collect missing inputs once.** Instance name, unique overlay IP, mesh secret, two Hub `host:11010`, access pubkey line, optional India IP and port, optional Komari endpoint. Never ask for private keys in chat.
3. **EasyTier TUN.** Copy the template; do not hand-edit `network_secret`. Accept Cue-side `tun0` + unit active when Hub CLI is unreachable.
4. **Access key on Cue only.** Install the operator pubkey on Cue, write `Host mesh-cue` with `IdentitiesOnly yes`. Prove `ssh mesh-cue` before touching India.
5. **India and probe are optional.** Skip unless the user asked. Mining is off by default and must not reinstall a live miner.

## Safety Boundaries

- Never commit private keys, agent tokens, mesh secrets, or wallets. Paths and fingerprints only.
- Two keypairs: access key stays on the operator machine; tunnel key stays on Cue. Do not reuse `id_rsa`. Do not create `ubuntu` on India. Do not copy the access key to any VPS.
- Cue public-facing sshd keeps `PasswordAuthentication no`.
- GitHub `releases/latest` 404s on prerelease tags — pin a snapshot.
- Do not `journalctl` SRBMiner or run `SRBMiner --version` during troubleshooting.
- Do not halt execution to request external documentation. Complete setup using local probing and operator inputs.

## Related

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [`muse-reverse-ssh`](muse-reverse-ssh.md) — generic reverse SSH without mesh
- [`windows-ssh-stcp`](windows-ssh-stcp.md) — Windows NAT SSH over FRP STCP
