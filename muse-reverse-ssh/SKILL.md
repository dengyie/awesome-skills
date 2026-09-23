---
name: muse-reverse-ssh
description: Use when exposing a machine without a public IP (cloud VM, container, home server) as a publicly reachable SSH server via a reverse SSH tunnel through a VPS; setting up a persistent keepalive supervisor for the tunnel; or diagnosing dropped tunnels, GatewayPorts binding failures, and forwarded-port access problems.
---

# Muse Reverse SSH

## Core Principle

The inner machine dials out; the VPS only forwards.

A reverse tunnel (`ssh -R <REMOTE_PORT>:localhost:22`) makes the VPS listen on a public port and forward everything to the inner machine's sshd. The inner network needs no inbound firewall rules and no public IP. Treat the tunnel itself as the server: if the tunnel process dies, the "server" is unreachable even though both machines are healthy. Monitor and keepalive the tunnel, not just the machines.

## Decision Tree

```text
Inner machine already has a public IP, or you control inbound port forwarding on its router?
  -> Run sshd directly with firewall rules. Do not add a reverse tunnel.

You need HTTPS/browser access to inner services, not just SSH?
  -> Prefer Cloudflare Tunnel or an nginx reverse proxy on the VPS.

Only your own devices need access (no public exposure)?
  -> Prefer Tailscale or WireGuard over a publicly forwarded port.

Inner machine cannot accept inbound connections, but must be SSH-reachable from the internet?
  -> Use this skill.
```

## Roles and Keypairs

Two machines, two keypairs. Never reuse one keypair for both directions:

| Keypair | Private key lives on | Public key goes to | Purpose |
| --- | --- | --- | --- |
| Tunnel | inner machine (`~/.ssh/tunnel-key`) | VPS user's `~/.ssh/authorized_keys` | inner machine authenticates TO the VPS to establish the tunnel |
| Access | operator's laptop (`access-key.pem`) | inner machine user's `~/.ssh/authorized_keys` | operator authenticates THROUGH the forwarded port to the inner machine |

Generate both with `ssh-keygen -t ed25519 -f <name> -N ""` and keep private keys at mode `600`.

## Preflight

Run before changing anything; keep the output for the final report.

On the VPS (root or sudo):

```bash
ss -tlnp | grep <REMOTE_PORT> || echo "port <REMOTE_PORT> free"
grep -E "^GatewayPorts" /etc/ssh/sshd_config || echo "GatewayPorts not set"
```

On the inner machine:

```bash
systemctl is-active sshd || service ssh status
ss -tlnp | grep ':22 ' || echo "nothing listening on 22"
id <INNER_USER> 2>/dev/null || echo "user <INNER_USER> missing"
```

Interpretation:

- Port already listening on the VPS: pick another `<REMOTE_PORT>` or stop the occupying process.
- `GatewayPorts` not set (or `no`): remote forwards bind to `127.0.0.1` only — the port will NOT be publicly reachable until fixed (see VPS Setup).
- Nothing on inner port 22: install and start openssh-server first.

## VPS Setup (one time)

1. Create the tunnel user (skip if it exists):

   ```bash
   id <VPS_USER> 2>/dev/null || useradd -m -s /bin/bash <VPS_USER>
   mkdir -p /home/<VPS_USER>/.ssh && chmod 700 /home/<VPS_USER>/.ssh
   ```

2. Install the tunnel public key:

   ```bash
   cat tunnel-key.pub >> /home/<VPS_USER>/.ssh/authorized_keys
   chmod 600 /home/<VPS_USER>/.ssh/authorized_keys
   chown -R <VPS_USER>:<VPS_USER> /home/<VPS_USER>/.ssh
   ```

3. Allow public binding of forwarded ports. In `/etc/ssh/sshd_config` set:

   ```text
   GatewayPorts yes
   ```

   then `systemctl reload sshd`. (Safer alternative: `GatewayPorts clientspecified` — see Safety Boundaries.)

4. Open `<REMOTE_PORT>`/tcp in the VPS firewall (ufw / cloud security group).

## Inner Machine Setup (one time)

1. Install and start openssh-server:

   ```bash
   sudo apt-get install -y openssh-server
   sudo systemctl enable --now ssh
   ```

2. Create the login user and install the access public key:

   ```bash
   id <INNER_USER> 2>/dev/null || sudo useradd -m -s /bin/bash <INNER_USER>
   sudo -u <INNER_USER> mkdir -p /home/<INNER_USER>/.ssh
   cat access-key.pub | sudo tee -a /home/<INNER_USER>/.ssh/authorized_keys >/dev/null
   sudo chmod 700 /home/<INNER_USER>/.ssh
   sudo chmod 600 /home/<INNER_USER>/.ssh/authorized_keys
   sudo chown -R <INNER_USER>:<INNER_USER> /home/<INNER_USER>/.ssh
   ```

3. Harden sshd (`/etc/ssh/sshd_config`):

   ```text
   PermitRootLogin prohibit-password
   PasswordAuthentication no
   ```

   then `sudo systemctl reload ssh`.

4. Place the tunnel private key:

   ```bash
   install -m 600 tunnel-key ~/.ssh/tunnel-key
   ```

## Keepalive

The tunnel must survive network drops, not just machine reboots. Run a user-level supervisor (template: `scripts/reverse-ssh-keepalive.sh`):

```bash
nohup ./reverse-ssh-keepalive.sh >/dev/null 2>&1 &
```

Key options and why they matter:

- `-N`: no remote command, forward only.
- `-R <REMOTE_PORT>:localhost:22`: the reverse forward itself.
- `-o ServerAliveInterval=20 -o ServerAliveCountMax=3`: detect a dead TCP connection within ~60s instead of hanging forever on a half-open socket.
- `-o ExitOnForwardFailure=yes`: fail fast if the VPS port cannot be bound (e.g. already taken) instead of sitting on a tunnel that forwards nowhere.
- `-o BatchMode=yes -o ConnectTimeout=20`: never prompt for input, never hang on connect.
- `flock -n` on a lock file: single instance. Takeover is kill-and-restart: the lock is held only by the supervisor, children must not inherit the lock fd, so killing the supervisor always releases it.
- Write the operator-facing endpoint to a file (e.g. `current-endpoint.txt`) so the access command stays discoverable:

  ```text
  ssh -p <REMOTE_PORT> -i access-key.pem <INNER_USER>@<VPS_IP>
  ```

## Boot Persistence

The keepalive supervisor only survives network drops. A machine reboot kills it silently — `nohup ... &` does not persist across boots, and without autostart the "server" stays down after every reboot with no alert. This is the most common cause of a tunnel that "just stops working" days later. Protect three layers independently:

### Layer 1 — process supervision (ssh dies, machine stays up)

Covered by `scripts/reverse-ssh-keepalive.sh` (flock-guarded restart loop). Alternatively, `autossh` is a drop-in replacement:

```bash
autossh -M 0 -N -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -o ExitOnForwardFailure=yes -i tunnel-key.pem \
  -R 0.0.0.0:<REMOTE_PORT>:localhost:22 <TUNNEL_USER>@<VPS_IP>
```

`-M 0` disables autossh's legacy monitor port and relies on SSH keepalives. Either way, something must (re)start the supervisor itself after a reboot — that is layer 2.

### Layer 2 — boot autostart (machine reboots, disk persists)

Pick the mechanism the platform actually persists (template: `scripts/reverse-ssh-boot.service`):

| Platform | Mechanism |
|---|---|
| systemd (most Linux servers / VPS) | unit file + `systemctl enable`, `Restart=always` |
| Linux without systemd | `@reboot` cron entry, or executable `/etc/rc.local` |
| macOS | `launchd` plist in `~/Library/LaunchAgents` with `RunAtLoad` |
| Windows | Task Scheduler task with an "At startup" trigger |

Pitfalls:

- `HOME` must resolve to the home holding the script, keys, and state dir. A unit running as root gets `HOME=/root` by default, which silently breaks every `$HOME`-relative path. Set `Environment=HOME=...` explicitly.
- The keepalive's `flock` guard makes boot restarts safe: the lock is released when the old process dies (and children never inherit it via `9>&-`), so a fresh instance after an unclean shutdown always takes over cleanly instead of exiting as "another instance running".

### Layer 3 — ephemeral machines (disk resets on reboot)

Containers, reset-on-boot VMs, and spot instances wipe the root filesystem on reboot: no unit file, no cron entry, no installed package survives — only a designated data disk persists, if any. Layer 2 cannot work there because there is nothing durable left to trigger it. Use instead:

- **Idempotent restore script on the persistent disk.** One script that reinstalls packages, recreates users and keys, and restarts the keepalive — and is safe to run repeatedly (`id <user> || useradd ...`, `apt-get install -y` is idempotent, kill-and-restart supervisors rather than start-if-absent).
- **External watchdog.** A scheduler or monitor *outside* the ephemeral machine polls for liveness and runs the restore path when it goes dark. Detection latency equals the poll interval — state that honestly instead of promising instant recovery.
- **VPS-side detection.** The VPS is usually a normal persistent machine. A tiny check there — `ss -tlnp | grep <REMOTE_PORT>` or a TCP connect attempt against the forwarded port — notices the tunnel disappearing before any human does, and is the cheapest layer-3 signal.

Verify each layer separately: kill the tunnel ssh (layer 1), reboot the machine (layer 2), and for ephemeral setups simulate a full reset and confirm the watchdog restores service within one poll interval (layer 3).

## Verification

From a third machine (the operator's laptop):

```bash
ssh -p <REMOTE_PORT> -i access-key.pem <INNER_USER>@<VPS_IP> 'hostname; whoami'
```

On the VPS, confirm the public listener:

```bash
ss -tlnp | grep <REMOTE_PORT>   # expect 0.0.0.0:<REMOTE_PORT>
```

On the inner machine, confirm exactly one tunnel process:

```bash
pgrep -f "ssh.*-R <REMOTE_PORT>:localhost:22" | wc -l   # expect 1
```

Then kill the tunnel ssh once and confirm it reconnects within ~10s and the endpoint works again.

Finally, reboot the inner machine (or restart the boot unit) and confirm the tunnel and endpoint recover without manual intervention — this is the test that catches missing boot persistence.

## Safety Boundaries

- `GatewayPorts yes` is global on the VPS: any user with ssh access can bind public ports. Prefer `GatewayPorts clientspecified` with an explicit `-R 0.0.0.0:<REMOTE_PORT>:...`, or restrict the port with firewall source-IP rules.
- The forwarded port is public: anyone on the internet can attempt SSH. Key-only auth (`PasswordAuthentication no`) is mandatory, not optional. Consider restricting source IPs at the VPS firewall.
- `StrictHostKeyChecking=no` with `UserKnownHostsFile=/dev/null` (used when the VPS is frequently reimaged) disables MITM protection for the tunnel leg. Accept it only for the tunnel leg, never for the operator access leg.
- Never store either private key in a repo, doc, or chat. Reference paths only.
- If the VPS is reimaged, the tunnel user's `authorized_keys` must be restored before the tunnel can reconnect — keep the tunnel public key somewhere durable.

## Failure Modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ssh -p <PORT>` times out from outside | VPS firewall blocks the port, or `GatewayPorts` is not `yes` (bound to 127.0.0.1) | open the firewall; set `GatewayPorts yes` and reload sshd |
| Tunnel connects but forwards nowhere | port already bound on the VPS; without `ExitOnForwardFailure` ssh stays up silently | add `ExitOnForwardFailure=yes`; pick a free port |
| Tunnel hangs after a network blip, never recovers | no liveness probing on a half-open TCP connection | `ServerAliveInterval` / `ServerAliveCountMax` plus the supervisor loop |
| Two tunnel processes fight over the port | duplicate keepalive instances | `flock -n` single-instance guard; kill-and-restart for takeover |
| Tunnel never comes back after a reboot | no boot autostart; `nohup &` does not survive reboots | systemd unit or `@reboot` cron (see Boot Persistence); verify with a real reboot |
| `Permission denied (publickey)` on the tunnel leg | tunnel public key missing from the VPS user's `authorized_keys` | reinstall `tunnel-key.pub` |
| `Permission denied (publickey)` on the access leg | access public key missing from the inner user's `authorized_keys` | reinstall `access-key.pub` |
