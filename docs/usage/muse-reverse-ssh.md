# Muse Reverse SSH

Use `muse-reverse-ssh` when a machine without a public IP (cloud VM, container, home server) must be SSH-reachable from the internet, and its network cannot accept inbound connections.

A reverse tunnel makes the inner machine dial out to a VPS; the VPS listens on a public port and forwards it back to the inner machine's sshd. No inbound firewall rules are needed on the inner network, and the inner machine needs no public IP.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- ssh into a cloud VM, container, or home machine that has no public IP
- keep the tunnel alive across network blips with automatic reconnect
- diagnose a reverse tunnel that connects but forwards nowhere, or a forwarded port that is not publicly reachable
- separate the tunnel credential from the operator login credential cleanly

Do not use it when the machine already has a public IP (run sshd directly with firewall rules), when you need HTTPS or browser access to inner services (consider Cloudflare Tunnel or an nginx reverse proxy on the VPS), or when only your own devices need access with no public exposure (consider Tailscale or WireGuard).

## Safety Boundaries

- The forwarded port is public: anyone on the internet can attempt SSH. Key-only auth (`PasswordAuthentication no`) is mandatory, and source-IP firewall restrictions are strongly recommended.
- `GatewayPorts yes` on the VPS is global; prefer `clientspecified` or firewall scoping.
- Never commit either private key to a repo, doc, or chat; reference paths only.
- `StrictHostKeyChecking=no` is acceptable for the tunnel leg when the VPS is frequently reimaged, never for the operator access leg.

## Workflow

1. Preflight both machines: confirm the VPS port is free and `GatewayPorts` state; confirm sshd listens on the inner machine.
2. On the VPS: create the tunnel user, install the tunnel public key, set `GatewayPorts yes`, reload sshd, open the port in the firewall.
3. On the inner machine: install openssh-server, create the login user, install the access public key, harden sshd (`PermitRootLogin prohibit-password`, `PasswordAuthentication no`), place the tunnel private key at mode `600`.
4. Install `scripts/reverse-ssh-keepalive.sh`, replace the placeholders, start it with `nohup`.
5. Add boot persistence: install `scripts/reverse-ssh-boot.service` (or a `@reboot` cron entry) so the tunnel survives machine reboots — `nohup` alone does not. Remember `Environment=HOME=...` when the unit runs as a different user.
6. Verify from a third machine through the public endpoint; kill the tunnel ssh once and confirm it reconnects and the endpoint works again; then reboot the inner machine and confirm everything recovers without manual intervention.

## Boot Persistence

The keepalive script from step 4 only survives network drops. A machine reboot kills it silently — `nohup ... &` does not persist across boots, and without autostart the tunnel stays down after every reboot with no alert. This is the most common reason a tunnel "just stops working" days later. Do not skip this section. Protect three layers:

**Layer 1 — process supervision.** If the ssh tunnel itself drops while the machine stays up, the keepalive script (or `autossh -M 0` as an alternative) restarts it. This is step 4.

**Layer 2 — boot autostart.** For machines whose disk survives reboots, register the keepalive to start at boot:

- **systemd** (most Linux servers/VPS): copy `muse-reverse-ssh/scripts/reverse-ssh-boot.service` to `/etc/systemd/system/`, replace `OPERATOR_USER` and the `HOME` path, then `sudo systemctl daemon-reload && sudo systemctl enable --now reverse-ssh-boot.service`.
- **No systemd**: a `@reboot` cron entry (`@reboot /home/<USER>/.reverse-ssh/reverse-ssh-keepalive.sh`), an executable `/etc/rc.local`, a macOS `launchd` plist with `RunAtLoad`, or a Windows Task Scheduler "At startup" task.

Watch out for:

- `HOME` must point at the home holding the script, keys, and state dir. A unit running as root gets `HOME=/root` by default, which silently breaks every `$HOME`-relative path in the keepalive script. Set `Environment=HOME=...` explicitly in the unit.
- The keepalive's `flock` single-instance guard makes boot restarts safe: the lock is released when the old process dies, so a fresh instance after an unclean shutdown takes over cleanly instead of exiting as "another instance running".

**Layer 3 — ephemeral machines.** Containers, reset-on-boot VMs, and spot instances wipe the root filesystem on reboot: no unit file, no cron entry, no installed package survives. Boot autostart cannot work there because there is nothing durable left to trigger it. Instead:

- Keep a single **idempotent restore script on the persistent disk** — one script that reinstalls packages, recreates users/keys, and restarts the keepalive, safe to run repeatedly.
- Run an **external watchdog** (a scheduler or monitor outside the ephemeral machine) that polls for liveness and runs the restore script when the tunnel goes dark. Recovery takes about one poll interval — plan for that honestly.
- Add **VPS-side detection**: the VPS is usually a normal persistent machine, so a tiny check there (`ss -tlnp | grep <REMOTE_PORT>`) notices the forwarded port disappearing before any human does.

## Verification

- `ssh -p <REMOTE_PORT> -i access-key.pem <INNER_USER>@<VPS_IP>` reaches the inner machine.
- `ss -tlnp | grep <REMOTE_PORT>` on the VPS shows `0.0.0.0:<REMOTE_PORT>`.
- Exactly one tunnel ssh process on the inner machine; it recovers within ~10s after being killed.
- The endpoint file (`current-endpoint.txt`) contains the working access command.
- Reboot the inner machine and confirm the tunnel and endpoint recover without manual intervention — this is the test that catches missing boot persistence (layer 2).
- For ephemeral machines: simulate a full reset and confirm the external watchdog restores service within one poll interval (layer 3).

## Failure Modes

See `SKILL.md` for the full table: public-port timeouts (`GatewayPorts` / firewall), tunnels that connect but forward nowhere (`ExitOnForwardFailure`), half-open hangs (`ServerAliveInterval`), duplicate keepalive instances (`flock -n`), `publickey` denials on either leg, and tunnels that never come back after a reboot (missing boot persistence).
