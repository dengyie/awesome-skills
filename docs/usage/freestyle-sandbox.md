# Freestyle Sandbox Access and Dynamic Dispatch

Use `freestyle-sandbox` when running code, testing scripts, building container images, or running isolated workloads on Freestyle.sh Linux cloud virtual machines.

The skill provides dynamic machine sizing (2 vCPU / 4 GiB vs 4 vCPU / 8 GiB), automatic idle timeouts, existing instance reuse, and guaranteed exit/interrupt cleanup hooks (`pause`) to strictly protect monthly compute quota limits.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- run Linux-native tasks, Python scripts, CLI tools, or untrusted code in an isolated cloud sandbox
- build Docker containers, C++/Rust binaries, or run heavy compilation on 4-core AMD64 Linux without draining Mac battery
- expose temporary Web APIs or webhook receivers with free automatic HTTPS subdomains (`*.style.dev`)
- ensure VMs are paused immediately upon task completion or cancellation to prevent compute quota depletion

Avoid when the task requires a permanent 24/7 background server (e.g. mining, continuous monitoring, probe host), or requires huge persistent egress bandwidth (>25 GB/month).

## How It Works

```text
               ┌── Task Workload Analysis ──┐
               │                            │
       [Lightweight / Script Test]    [Heavy Build / Docker Pack]
               │                            │
      Tier: sm (2 vCPU / 4 GiB)     Tier: std (4 vCPU / 8 GiB)
      Image: ubuntu-sm              Image: ubuntu
      Idle timeout: 600s            Idle timeout: 300s
      Budget: ~50h/month            Budget: ~25h/month
               │                            │
               └──► Probe Existing VMs ◄────┘
                          │
       ┌──────────────────┴──────────────────┐
   [Existing paused VM]                [No matching VM]
           │                                 │
     Resume instantly                   Create with idle timeout
           │                                 │
           └────────► Execute Task ◄─────────┘
                          │
                 【Pause on Exit/Interrupt】
               (Files preserved, compute metered stops)
```

## What's Bundled

- `SKILL.md` — Core instructions, dynamic task decision matrix, and strict lifecycle guidelines.
- `references/decision-matrix.md` — Sizing matrix, monthly compute budget breakdown, and policy reference.
- `scripts/manage.sh` — Hardened management helper with signal traps (`INT`/`TERM`/`EXIT`), array-based argument passthrough, state polling, and automatic pause.
- `agents/openai.yaml` — Agent metadata interface definition.

## Quick CLI Examples

```bash
# Run a one-off command with automatic resume -> execute -> pause
./freestyle-sandbox/scripts/manage.sh run sandbox-sm sm "python3 -c 'print(\"Hello Sandbox\")'"

# Ensure an environment is running for interactive SSH / VS Code
./freestyle-sandbox/scripts/manage.sh ensure sandbox-sm sm

# Manually pause to freeze compute metering
./freestyle-sandbox/scripts/manage.sh pause sandbox-sm
```
