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
- **Offline package cache for the restore path.** On reset-prone machines, `apt-get update/install` is the slowest and flakiest part of a restore (network, mirror issues, the platform's own apt reconciliation holding the lock). Pre-download the needed `.deb`s plus their dependency closure onto the persistent disk (`apt-cache depends --recurse --no-recommends ... <pkg> | apt-get download`), refresh on a schedule; the restore script installs with `dpkg -i <cachedir>/*.deb` first and only falls back to apt when the cache is missing or incomplete. Measured on a real reset-prone VM: ~7s offline vs 2–4 min via apt — recovery is then dominated by detection latency alone.
- **External watchdog.** A scheduler or monitor *outside* the ephemeral machine polls for liveness and runs the restore path when it goes dark. Detection latency equals the poll interval — state that honestly instead of promising instant recovery. A 1-minute poll is a good default: detection within ~1 min, recovery dominated by the restore script itself (2–4 min), so total downtime per incident is typically under 5 minutes. Polling faster (e.g. every 30s) barely shortens recovery while doubling check cost and raising the chance of catching a transient self-healing moment (tunnel reconnect, sshd restart) and triggering a needless restore.
  - Guard the restore path with a single-instance lock *inside* the restore script: if a restore is already running, the new check exits silently instead of stacking restores. Use an atomic `mkdir` lockdir: `mkdir <restore.lockdir>` wins the race, and the holder records its PID + start timestamp in a file inside. On contention, check `/proc/<pid>/cmdline` — if the recorded PID is still the restore script and the lock is fresh, exit quietly; if the PID is dead or the lock is older than your max restore time, delete the lockdir (stale lock) and retry. Clean up with `trap 'rm -rf <restore.lockdir>' EXIT`. Do **not** wrap the script in an outer `flock -n <restore.lock>` — see the pitfall below.
  - Check more than the tunnel: the tunnel ssh process (`pgrep -f "[s]sh.*-R <REMOTE_PORT>"` — note the bracket trick below), `sshd`, the supervisor script itself, and — for agents that can hang silently — log freshness (restart the agent if its log hasn't grown in N minutes).
- **VPS-side detection.** The VPS is usually a normal persistent machine. A tiny check there — `ss -tlnp | grep <REMOTE_PORT>` or a TCP connect attempt against the forwarded port — notices the tunnel disappearing before any human does, and is the cheapest layer-3 signal.

### Watchdog and restore pitfalls (learned the hard way)

- **Never guard the restore script with an outer `flock -n <restore.lock>`.** This was the old advice in this very skill — and it silently disabled a production watchdog for ~2.5 hours before anyone noticed. The flock file descriptor is inherited by every long-lived daemon the restore script starts (keepalive, agent, ssh), so the advisory lock is held forever by those background processes and never released; every later watchdog run then believes "a restore is already in progress" and quietly skips recovery. The watchdog keeps polling, logging healthy runs, but can never recover anything again. Fix: put the mutual exclusion *inside* the restore script as an atomic `mkdir` lockdir — a directory cannot be inherited by children, so it can only be held by the script itself — with PID/timestamp stale-lock reclaim (see the Layer 3 bullet above). Note this is the opposite situation from the keepalive supervisor, where `flock -n 9` plus `9>&-` is correct: there the lock is held by one short-lived supervisor, children are explicitly denied the fd, and kill-and-restart releases it.
- **`pgrep -f` matches the checker itself.** `pgrep -f "ssh.*-R <REMOTE_PORT>"` also matches the very command running the check, because the pattern text appears in the checker's own command line — a dead tunnel then looks healthy forever. Use the bracket trick: `pgrep -f "[s]sh.*-R <REMOTE_PORT>"`. The regex `[s]sh` matches `ssh` in the target but not the literal `[s]sh` in your own command line. (Same reason supervisor self-checks use `[/]`, as in `pgrep -f "[/]keepalive.sh"`.)
- **PIDs get reused after a reboot.** A pidfile alone can lie: after a reset, an unrelated process may hold the recorded PID. When validating a pidfile, also compare `/proc/<pid>/cmdline` against the expected program name before trusting it — and before killing it.
- **Never `pkill -f <supervisor-name>` to stop supervisors.** The pattern matches your own management shell when its command line contains the name (e.g. you launched the restore from a shell whose command includes it), killing your own session mid-restore. Stop via the pidfile: read the PID, verify `/proc/<pid>/cmdline`, then `kill` exactly that PID. (Same self-match hazard as the `pgrep` pitfall above — the bracket trick works for `pkill` too.)
- **`dpkg -i` can still ask questions.** Reinstalling a package whose config file you modified (e.g. `sshd_config`) makes `ucf` prompt interactively about which version to keep — under a non-interactive restore this hangs forever (observed: stuck 7+ min in `openssh-server.postinst`). Always run restore installs as `DEBIAN_FRONTEND=noninteractive dpkg --force-confdef --force-confold -i ...`.
- **After a platform reboot, `apt`/`dpkg` may be locked** by the platform's own reconciliation for several minutes. A restore script that fails on the lock turns one outage into two. Loop-wait on the lock (e.g. up to ~10 min, checking every 30s) before giving up.
- **Supervisors should also watch `sshd`.** If the tunnel supervisor notices `sshd` gone but the `sshd` binary still exists, restarting sshd directly is a seconds-level fix — no full restore needed.

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
| Watchdog never fires even though the tunnel is dead | `pgrep -f "ssh.*-R <PORT>"` matches the checker's own command line | use the bracket trick: `pgrep -f "[s]sh.*-R <PORT>"` |
| Restore fails right after a reboot with apt/dpkg lock errors | platform reconciliation holds the package lock for minutes after boot | loop-wait on the lock (up to ~10 min) instead of failing immediately |
| Restore kills your own SSH session mid-run | `pkill -f <supervisor-name>` matched your management shell's command line | stop supervisors via pidfile + `/proc/<pid>/cmdline` verification, never broad `pkill -f` |
| `Permission denied (publickey)` on the tunnel leg | tunnel public key missing from the VPS user's `authorized_keys` | reinstall `tunnel-key.pub` |
| `Permission denied (publickey)` on the access leg | access public key missing from the inner user's `authorized_keys` | reinstall `access-key.pub` |
