# Render Engine Web-Box Operations

Use `render-engine` when deploying, maintaining, diagnosing, or troubleshooting Linux Web-Box containers on Render.com Free Tier (Docker Web Services) with single-port Caddy multiplexing, EasyTier user-space network mesh, persistent ttyd+tmux terminals, and optional Komari telemetry.

The skill provides an operational runbook and diagnostic standard operating procedure (SOP) tailored for AI agents and human operators. It addresses specific constraints of the Render Free Tier (AWS us-east Kubernetes, 512MB RAM cap, no `/dev/net/tun`, single public port, 15-minute HTTP idle spindown, and OverlayFS host disk metric leakage).

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- Deploy a zero-config or modular Linux environment on Render.com free Docker service
- Connect an unprivileged container without `/dev/net/tun` to an EasyTier mesh via `--no-tun --use-smoltcp`
- Route multiple services (health checks, Web terminal, EasyTier WebSocket, sing-box VLESS) over a single public port (`$PORT:10000`) using Caddy
- Provide persistent, disconnect-resilient Web terminal sessions (`ttyd` + `tmux` session `main`) with active WebSocket keepalive (`--ping-interval 15`)
- Investigate false disk capacity alarms caused by Kubernetes OverlayFS host storage leakage
- Triage container spindown, offline incidents, and health-check monitoring via Uptime bots

Avoid when deploying on dedicated virtual machines with full root kernel privileges (where native kernel TUN and systemd are preferred), or when deploying on Windows machines behind NAT (use `windows-ssh-stcp`).

## How It Works

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

- `SKILL.md` — The complete agent operating procedure: environment discovery, modular feature activation, terminal persistence, and structured diagnostics.
- `references/deployment.md` — Platform specification, 512MB RAM constraints, environment variable matrix, and `render.yaml` blueprint.
- `references/network-mesh.md` — Technical details of EasyTier user-space `smoltcp` networking, dynamic connector commands, and mesh topology.
- `references/terminal-persistence.md` — Root-cause analysis of edge WebSocket idle drops, `--ping-interval 15` keepalive, and `ttyd` + `tmux` session persistence.
- `references/troubleshooting.md` — Incident runbooks for OverlayFS false disk alarms, offline recovery, BasicAuth issues, and circuit breaker watchdog crashes.

## Quick Workflow

1. **Deployment**: Deploy via Render Blueprint (`render.yaml`) or Dockerfile. Zero environment variables required for minimal secure Web-Box; passwords auto-generate on launch.
2. **Modular Activation**: Add `ET_PEERS`, `ET_SECRET`, and `ET_NAME` to join EasyTier mesh. Add `KOMARI_ENDPOINT` and `KOMARI_TOKEN` to activate telemetry.
3. **Web Terminal Access**: Access `https://<service-name>.onrender.com/shell/` with BasicAuth. Terminal auto-attaches to the persistent `main` tmux session.
4. **Mesh Access**: Connect directly via bastion: `ssh -o ProxyJump=pxed root@10.144.144.90`.
5. **Diagnostics**: For false disk alarms (e.g. reporting 315GB / 386GB used), verify real container usage with `du -sh /` (~190MB) and ignore the OverlayFS host leak, or set `AGENT_FORCE_DISK_TOTAL="5368709120"` in telemetry.
