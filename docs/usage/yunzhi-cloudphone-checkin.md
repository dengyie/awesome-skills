# Yunzhi Cloudphone Checkin

Use `yunzhi-cloudphone-checkin` when you need automated daily check-in and cloud phone space benefit card renewal (benefitConfigId: 158) for Tianyi / Play.cn Yunzhi Cloudphone (`https://yunzhi.play.cn/ai/?channel_code=00000042`).

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- automatically claim the daily login popup card (2 days cloud phone space) and bind it to the running cloud device
- share an instant, zero-dependency one-click check-in script with friends via browser DevTools Console
- run scheduled daily check-ins via Chrome DevTools Protocol (CDP) on macOS, Linux, or Windows without WAF 503 blocks
- execute headless check-ins on Linux VPS / Docker containers with token-based CLI authentication

Avoid when you are trying to manage Android system packages or ADB tunnels on the device (use `cloudphone-adb-tunnel` instead).

## How It Works

```text
[Browser Console] (Zero Dependency)
    → window.fetch + WebCrypto HMAC-SHA256 & in-page MD5
    → In-page execution with native browser TLS fingerprint (100% WAF pass)

[Local Chrome CDP] (Recommended for Automation)
    → python3 yunzhi_checkin.py --cdp http://127.0.0.1:9222
    → Auto-extracts JWT token from localStorage['cloud_phone_token']
    → Executes API calls via in-page fetch evaluation

[Direct HTTP / Headless CLI]
    → python3 yunzhi_checkin.py --token <JWT>
    → Computes MD5 body signature + HMAC-SHA256 head signature
    → Automatic curl_cffi Chrome 120 TLS fingerprint simulation
```

## What's Bundled

The skill is self-contained and sanitized — credentials stay with the operator:

- `scripts/browser_console_one_click.js` — pure JavaScript one-click checkin script for browser DevTools console (with pure JS MD5, WebCrypto HMAC-SHA256, and colorful console status output).
- `scripts/yunzhi_checkin.py` — production Python CLI supporting `--cdp`, `--token`, `--smoke` (dry run), `--json` (webhook / automation output), and automatic tab lifecycle cleanup.
- `scripts/capture_traffic.py` — CDP traffic sniffer and debugger for protocol analysis with automatic credential redaction.
- `references/protocol.md` — complete reverse-engineered protocol schema, dual-signature mathematics, Qu header exclusion table, and verified test vectors.
- `references/pitfalls.md` — runbook covering Edge WAF HTTP 503 TLS fingerprinting, message queue asynchronous card issuance delay, and 64-bit integer precision.
- `tests/test_signatures.py` — offline unit test suite validating signature vectors and zero credential leak guards.

## Execution Modes

1. **Browser Console One-Click (Best for Sharing)**:
   - Log into `https://yunzhi.play.cn/ai/?channel_code=00000042`.
   - Open Developer Tools (`F12` or `Cmd + Opt + I`) -> Console.
   - Paste `scripts/browser_console_one_click.js` and hit Enter.
2. **Chrome CDP Automation**:
   - Start Chrome with `--remote-debugging-port=9222`.
   - Run `python3 scripts/yunzhi_checkin.py --cdp http://127.0.0.1:9222`.
3. **Direct CLI / Server**:
   - Extract token: `copy(localStorage.getItem('cloud_phone_token'))` in console.
   - Run `python3 scripts/yunzhi_checkin.py --token <JWT>`.

## Operational Notes

- The skill code contains no personal tokens, phone numbers, or account secrets.
- In-memory token renewal (`_authorization` header) is applied seamlessly.
- Device selection prioritizes `status == 2` (Active / Running) instances.

## Related

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
