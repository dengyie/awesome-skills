# Reverse SSH Server

Use `reverse-ssh-server` when a machine without a public IP (cloud VM, container, home server) must be SSH-reachable from the internet, and its network cannot accept inbound connections.

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
5. Verify from a third machine through the public endpoint; kill the tunnel ssh once and confirm it reconnects and the endpoint works again.

## Verification

- `ssh -p <REMOTE_PORT> -i access-key.pem <INNER_USER>@<VPS_IP>` reaches the inner machine.
- `ss -tlnp | grep <REMOTE_PORT>` on the VPS shows `0.0.0.0:<REMOTE_PORT>`.
- Exactly one tunnel ssh process on the inner machine; it recovers within ~10s after being killed.
- The endpoint file (`current-endpoint.txt`) contains the working access command.

## Failure Modes

See `SKILL.md` for the full table: public-port timeouts (`GatewayPorts` / firewall), tunnels that connect but forward nowhere (`ExitOnForwardFailure`), half-open hangs (`ServerAliveInterval`), duplicate keepalive instances (`flock -n`), and `publickey` denials on either leg.
