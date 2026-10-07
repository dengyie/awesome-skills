# Phone-Playwright

Use `phone-playwright` when controlling, inspecting, automating, or building AI agents for Android or iOS mobile devices with Playwright-style lazy locators, viewport-aware semantic distillation, auto-waiting actionability state machines, warm-cache fast dispatch, scroll_into_view, Chinese clipboard typing, or MCP stdio JSON-RPC mobile servers.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- enable AI agents (Claude, ZCode, Cursor) to reliably perceive and interact with real mobile devices (Android / iOS)
- prune bloated accessibility hierarchy XML trees into high-density, low-token `@index` semantic element maps (reducing LLM token usage by ≥90%)
- eliminate flaky clicks and transition race conditions via a strict 5-phase actionability auto-waiting state machine (`Attached -> Visible -> Stable -> Enabled -> Dispatch`)
- accelerate AI mobile interaction latency with a 1.0s TTL warm cache, bringing click dispatch down from 7640ms to ~140ms (54x speedup)
- automatically scroll long mobile pages to bring off-screen elements into view (`locator.scroll_into_view()`)
- reliably type Chinese characters, emojis, and shell metacharacters without keyboard IME mangling
- survive Wi-Fi ADB connection drops and dynamic port drift through mDNS heartbeat discovery

Avoid when automating desktop web browsers (use browser-use or standard Playwright instead) or when managing remote cloudphone reverse SSH/STCP tunnels (use `cloudphone-adb-tunnel` instead).

## How It Works

```text
[AI Agent / LLM / User Script]
    │  (MCP JSON-RPC 2.0 or Python Async/Sync SDK)
    ▼
[PhonePage / PhoneLocator]
    │  - Lazy evaluation
    │  - scroll_into_view()
    ▼
[Actionability State Machine]
    ├── 1.0s Snapshot Warm Cache (140ms fast path)
    └── 5-Phase Guard: Attached -> Visible -> Stable -> Enabled -> Dispatch
    ▼
[Semantic Pruner] ── O(N) DFS geometric clipping & label hoisting (90% token drop)
    ▼
[Hardware Drivers] ── Android ADB / iOS WDA (with mDNS Port Drift Watchdog)
```

## What's Bundled

The skill is completely self-contained:

- `SKILL.md` — skill definition, trigger keywords, architectural overview, and cheat sheet
- `src/phone_playwright/` — production-grade Python package with full async/sync SDK, drivers, and MCP server
- `scripts/cli.py` — versatile CLI utility supporting single-step actions (`snapshot`, `click`, `fill`, `scroll`, `swipe`), interactive REPL, and MCP stdio launcher
- `scripts/inspect_ui.py` — fast visual and compact element inspection tool
- `references/architecture.md` — deep architectural design, data flow diagrams, and state machine specifications
- `references/api-reference.md` — exhaustive API reference for PhonePage, PhoneLocator, selectors, and MCP tools
- `references/pitfalls.md` — real-world hardware pitfalls runbook (UiAutomator dump delay, port drift, Windows IOCP pipes, Chinese IME)
- `tests/` — offline automated test suite (27 unit tests verifying pruner, geometry, state machine, watchdog, and packaging)

## Quickstart

### 1. Interactive Device Inspection (CLI)

```bash
# Dump semantic element table from connected phone
python phone-playwright/scripts/cli.py --device 192.168.1.3:43037 snapshot

# Click element with auto-waiting
python phone-playwright/scripts/cli.py --device 192.168.1.3:43037 click "text=设置"

# Scroll off-screen element into view
python phone-playwright/scripts/cli.py --device 192.168.1.3:43037 scroll "text=关于本机"
```

### 2. Python Scripting

```python
import asyncio
from phone_playwright.api.async_api import AsyncPhonePlaywright

async def run():
    async with AsyncPhonePlaywright() as pw:
        page = await pw.connect("192.168.1.3:43037")
        snap = await page.snapshot()
        print(snap.summary_markdown)
        await page.locator("text=设置").click()
        await page.get_by_text("关于本机").scroll_into_view().click()

asyncio.run(run())
```

### 3. MCP Server for Agents

Launch the STDIO JSON-RPC 2.0 server directly:

```bash
python phone-playwright/scripts/cli.py --device 192.168.1.3:43037 mcp
```

## Production Hardening & Pitfalls

| Symptom | Root Cause | Built-in Fix |
|---|---|---|
| Clicks take 7+ seconds | Android `uiautomator dump` cold boot overhead | Snapshot warm-cache (1.0s TTL) skips dump on immediate action (~140ms) |
| Off-screen item times out | Deep list elements clipped outside viewport | Unclipped virtual viewport detects `OffscreenElementError`; `scroll_into_view()` scrolls into viewport |
| Chinese characters fail to type | ADB `input text` only accepts ASCII keycodes | Clipboard broadcast injection with `KEYCODE_PASTE` fallback |
| Windows MCP server crashes with WinError 6 | Windows IOCP pipe incompatibility | Non-blocking thread-pool executor standard input reader |
| Wi-Fi ADB loses connection on DHCP renew | Android 11+ dynamic wireless port drift | Fleet Watchdog probes mDNS `_adb-tls-connect._tcp` and updates route atomically |
