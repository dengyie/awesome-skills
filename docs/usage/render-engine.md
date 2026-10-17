# Render Engine Web-Box 0-to-1 Deployment & Operations

Use `render-engine` when guiding a user or agent through the complete lifecycle of deploying, configuring, and connecting to an unprivileged Linux Web-Box container on Render.com Free Tier: from initial Render.com account registration, Forking/Cloning the repository, configuring Blueprint / Web Service settings, deploying the container, to connecting via persistent `ttyd`+`tmux` Web Terminal and EasyTier mesh SSH.

The skill provides an operational runbook and diagnostic standard operating procedure (SOP) tailored for AI agents and human operators. It addresses specific constraints of the Render Free Tier (AWS us-east Kubernetes, 512MB RAM cap, no `/dev/net/tun`, single public port, 15-minute HTTP idle spindown, and OverlayFS host disk metric leakage).

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- Guide a user from scratch: registering on Render.com, Forking `dengyie/render-engine`, and deploying with 1-click Blueprint
- Deploy a zero-config or modular Linux environment on Render.com free Docker service
- Connect an unprivileged container without `/dev/net/tun` to an EasyTier mesh via `--no-tun --use-smoltcp`
- Route multiple services (health checks, Web terminal, EasyTier WebSocket, sing-box VLESS) over a single public port (`$PORT:10000`) using Caddy
- Provide persistent, disconnect-resilient Web terminal sessions (`ttyd` + `tmux` session `main`) with active WebSocket keepalive (`--ping-interval 15`)
- Connect and run commands inside the container via browser Web Terminal, mesh SSH, or headless agent WebSocket
- Investigate false disk capacity alarms caused by Kubernetes OverlayFS host storage leakage
- Triage container spindown, offline incidents, and health-check monitoring via Uptime bots

Avoid when deploying on dedicated virtual machines with full root kernel privileges (where native kernel TUN and systemd are preferred), or when deploying on Windows machines behind NAT (use `windows-ssh-stcp`).

## How It Works

```text
  Phase 0: Account Setup       Phase 1: Repo Setup         Phase 2: Configuration      Phase 3: Deploy & Verify    Phase 4: Connection
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ Register Render.com     │ │ Fork/Clone Repository   │ │ Set Environment Vars    │ │ Trigger Build & Deploy  │ │ Connect Web Shell / SSH │
│ (GitHub SSO, Free Tier) │►│ (dengyie/render-engine) │►│ (Credentials/Mesh/Probe)│►│ (Verify Build/Logs,     │►│ (ttyd+tmux persistent   │
│ (No credit card needed) │ │ (Automated CI/CD sync)  │ │ (Zero-config out of box)│ │  Extract random pass)   │ │  session or EasyTier) │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

Single-port multiplexing topology:
```text
Render Public Edge (Single Exposed $PORT:10000)
                  │
                  ▼
         Caddy Web Multiplexer
  ┌───────────────┬───────────────┬───────────────┬───────────────┐
  ▼               ▼               ▼               ▼               ▼
/health        /shell/          /et/*         /vless-ws/*      Others
(200 OK)    (ttyd + tmux)    (EasyTier WS)    (sing-box)      (404)
                  │
                  ▼
     /usr/local/bin/ttyd-session
                  │
                  ▼
         tmux (session: main)
                  │
                  ▼
              /bin/bash
```

Additionally, when EasyTier is active:
```text
Operator / Bastion (pxed)
          │
          ▼ (Virtual Mesh: 10.144.144.0/24)
  10.144.144.90 (render-box, smoltcp user-space stack)
    ├── TCP 22 / 2222 -> Local OpenSSH Server
    └── TCP 10808     -> Local sing-box SOCKS5/HTTP Proxy
```

## What's Bundled

The skill contains actionable operational runbooks and reference guides:

- `SKILL.md` — The complete agent operating procedure: 0-to-1 onboarding, Render registration, Forking repo, Blueprint deployment, log inspection, persistent terminal access, and structured diagnostics.
- `references/deployment.md` — Platform specifications, 512MB RAM constraints, environment variable matrix, console walkthrough, and `render.yaml` blueprint.
- `references/network-mesh.md` — Technical details of EasyTier user-space `smoltcp` networking, dynamic connector commands, and mesh topology.
- `references/terminal-persistence.md` — Root-cause analysis of edge WebSocket idle drops, `--ping-interval 15` keepalive, `ttyd` + `tmux` session persistence, and headless Python WebSocket script.
- `references/troubleshooting.md` — Incident runbooks for OverlayFS false disk alarms, offline recovery, BasicAuth issues, and circuit breaker watchdog crashes.

## Quick Workflow (0 to 1)

1. **Register**: Guide user to register at `https://dashboard.render.com/register` with GitHub. Explain Free Tier benefits (750 hours/mo, no credit card required).
2. **Repository**: Guide user to Fork `https://github.com/dengyie/render-engine` to their GitHub for CI/CD updates.
3. **Configure & Deploy**: Use Blueprint URL `https://render.com/deploy?repo=https://github.com/dengyie/render-engine` (or user's fork). Select Free plan, region, and optional environment variables (`SSH_PASS`, `ET_PEERS`, `KOMARI_ENDPOINT`).
4. **Log Verification**: In Render Dashboard Logs, verify Caddy, SSHD, and ttyd startup. If `SSH_PASS` was not manually set, copy the 18-character random password printed in the logs.
5. **Connect**:
   - Web Terminal: Open `https://<service-name>.onrender.com/shell/` with BasicAuth (`admin` / password). Auto-attaches to persistent `main` tmux session.
   - Mesh SSH: Connect via bastion `ssh -o ProxyJump=pxed root@10.144.144.90`.
6. **Maintenance & 24/7 Continuity**: Built-in self-keepalive (`ENABLE_KEEPALIVE=true`) automatically pings the service's own public edge URL every 5 minutes to prevent the 15-minute container spindown, staying comfortably within the 750 free hours/month quota. External ping via UptimeRobot or VPS Cron can be added as an optional fail-safe. For false disk alarms (~315GB / 386GB used), verify actual container usage (~191MB) and configure `KOMARI_FORCE_DISK_TOTAL="5368709120"`.
