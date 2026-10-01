#!/usr/bin/env python3
"""云智手机 (yunzhi.play.cn) 流量嗅探与协议抓包调试工具.

通过 CDP (Chrome DevTools Protocol) 挂载到浏览器实例，实时监听所有与云智手机
相关（yunzhi, play.cn, new-gm.cn）的 API 请求与响应，保存至本地 JSONL 文件。
严格遵守安全脱敏契约：Authorization/Cookie 等敏感头在落盘前自动截断脱敏。

使用方式：
  python3 capture_traffic.py [持续捕获秒数，默认 120]
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

OUT_FILE = Path("yunzhi_traffic_capture.jsonl")
MATCH_DOMAINS = ["yunzhi", "new-gm", "play.cn"]
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}


def redact_headers(headers: dict) -> dict:
    """脱敏敏感头，防止凭据意外泄漏进日志"""
    out = {}
    for k, v in (headers or {}).items():
        if k.lower() in SENSITIVE_HEADERS and isinstance(v, str) and len(v) > 20:
            out[k] = v[:10] + "..." + v[-6:]
        else:
            out[k] = v
    return out


async def main():
    timeout_s = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    print(f"[*] 启动 CDP 流量监听（持续 {timeout_s}s，输出文件: {OUT_FILE.resolve()}）...", flush=True)

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[-] 需要 playwright 依赖: pip install playwright", flush=True)
        sys.exit(1)

    cdp_url = os.environ.get("CDP_HTTP", "http://127.0.0.1:9222")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"[-] 无法连接到 Chrome CDP ({cdp_url}): {e}", flush=True)
            print("请确认 Chrome 已启动远程调试端口: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            sys.exit(1)

        async def handle_request(req):
            url = req.url
            if not any(d in url for d in MATCH_DOMAINS):
                return
            if any(ext in url for ext in [".png", ".jpg", ".jpeg", ".css", ".woff", ".svg", ".ico"]):
                return

            entry = {
                "time": datetime.now().isoformat(),
                "type": "request",
                "method": req.method,
                "url": url,
                "headers": redact_headers(dict(req.headers)),
                "post_data": req.post_data,
            }
            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f" -> [REQ] {req.method} {url[:80]}", flush=True)

        async def handle_response(resp):
            url = resp.url
            if not any(d in url for d in MATCH_DOMAINS):
                return
            if any(ext in url for ext in [".png", ".jpg", ".jpeg", ".css", ".woff", ".svg", ".ico"]):
                return

            body = ""
            try:
                body = await resp.text()
            except Exception:
                pass

            entry = {
                "time": datetime.now().isoformat(),
                "type": "response",
                "status": resp.status,
                "url": url,
                "headers": redact_headers(dict(resp.headers)),
                "body": body[:2000] if body else "",
            }
            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f" <- [RES] {resp.status} {url[:80]} ({len(body)} bytes)", flush=True)

        for ctx in browser.contexts:
            for page in ctx.pages:
                page.on("request", handle_request)
                page.on("response", handle_response)

        start_time = time.time()
        while time.time() - start_time < timeout_s:
            await asyncio.sleep(1)

        print(f"[+] 抓包完成，结果已保存至: {OUT_FILE.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
