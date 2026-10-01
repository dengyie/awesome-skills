#!/usr/bin/env python3
"""yunzhi (云智手机 https://yunzhi.play.cn) 自动化签到与权益领取独立脚本.

本脚本专为分享设计，支持多种执行模式：
1. 【推荐】CDP 模式 (Chrome DevTools Protocol)：
   自动连接本机已登录云智手机的 Chrome/Edge 浏览器，免输 Token，自动规避边缘 WAF/TLS 指纹拦截。
2. 直连模式 (Direct HTTP)：
   支持传入 Token (--token 或环境变量 YUNZHI_TOKEN)，在无桌面环境的服务器或容器中运行。
   若环境安装了 curl_cffi，会自动启用 Chrome 120 TLS 指纹模拟。
3. 只读烟测模式 (--smoke)：
   仅查询当前登录态、弹窗状态、待开通卡片与云机有效期，不执行任何消耗性领取操作。

使用示例：
  # CDP 模式自动签到（Chrome 需以 --remote-debugging-port=9222 启动并登录云智手机）
  python3 yunzhi_checkin.py --cdp http://127.0.0.1:9222

  # Direct HTTP 模式（传入 Token）
  python3 yunzhi_checkin.py --token "eyJhbGciOi..."

  # 只读状态检查（不领卡）
  python3 yunzhi_checkin.py --cdp http://127.0.0.1:9222 --smoke
  
  # 输出纯 JSON 结果（供自动化调度 / Webhook 消费）
  python3 yunzhi_checkin.py --cdp http://127.0.0.1:9222 --json
"""

import argparse
import asyncio
import hashlib
import hmac
import json
import os
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# ==================== 逆向核心常量与配置 ====================
YUNZHI_ENTRY_URL = "https://yunzhi.play.cn/ai/?channel_code=00000042"
YUNZHI_API_BASE = "https://yunzhi.new-gm.cn/yunzhi"
YUNZHI_BENEFIT_ID = "158"  # 云机空间服务（新开 2 天卡）
YUNZHI_SIGN_SALT = "7f9e2d08c1b5a3709e4f6d2a8c0e1b3f"
YUNZHI_HMAC_KEY = "8822FF81B6623e6f338d6F2A7F49DA83"
YUNZHI_VERSION = "10310"
YUNZHI_CHANNEL_CODE = "00000042"

# 参与头签名排除表（前端 Qu 表，键小写）
HMAC_EXCLUDED_HEADERS = frozenset({
    "content-length", "host", "connection", "accept-encoding", "user-agent",
    "sign", "content-type", "accept", "device_code", "model", "api_level",
    "cache-control",
})

# 浏览器页面内 Fetch 脚本
YUNZHI_FETCH_JS = """
async (p) => {
    try {
        const opt = { method: p.method, headers: p.headers, credentials: 'omit' };
        if (p.body !== null && p.body !== undefined) opt.body = p.body;
        const r = await fetch(p.url, opt);
        let data = null;
        try { data = await r.json(); } catch (e) { data = null; }
        let auth = '';
        try { auth = r.headers.get('authorization') || ''; } catch (e) {}
        return { _http_status: r.status, _authorization: auth, _data: data };
    } catch (e) {
        return { _http_status: 0, _authorization: '', _data: null, _err: String(e) };
    }
}
"""

# 从页面读取持久化凭据脚本
YUNZHI_CREDS_JS = """
() => {
    let token = '';
    try { token = localStorage.getItem('cloud_phone_token') || ''; } catch (e) {}
    if (!token) {
        try {
            const m = document.cookie.match(/(?:^|; )CG_CLINET_USER_TOKEN_YUN=([^;]*)/);
            if (m) token = decodeURIComponent(m[1]);
        } catch (e) {}
    }
    let deviceNo = '';
    try { deviceNo = localStorage.getItem('cloud_phone_device_no') || ''; } catch (e) {}
    return { token: token, deviceNo: deviceNo };
}
"""


# ==================== 签名算法实现 ====================

def generate_request_id() -> str:
    """生成 32 位 UUID-like 字符串（与前端 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx' 一致）"""
    tpl = "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx"
    hexch = "0123456789abcdef"
    out = []
    for ch in tpl:
        if ch == "x":
            out.append(random.choice(hexch))
        elif ch == "y":
            out.append(random.choice("89ab"))
        else:
            out.append(ch)
    return "".join(out)


def md5_body_sign(params: Dict[str, Any]) -> str:
    """体签名：MD5(除 sign 外非 null 参数 key 升序 k=v & 拼接 + 盐).
    
    与前端 ua()/Le() 逐字节一致。
    """
    items = {k: v for k, v in (params or {}).items() if k != "sign" and v is not None}
    qs = "&".join(f"{k}={items[k]}" for k in sorted(items))
    return hashlib.md5((qs + YUNZHI_SIGN_SALT).encode("utf-8")).hexdigest()


def canonicalize_headers(headers: Dict[str, Any]) -> str:
    """头规范化：键小写、剔除 Qu 排除表、按 key 升序 'k=v' & 拼接."""
    norm = {}
    for k, v in (headers or {}).items():
        if v is None:
            continue
        key_lower = str(k).lower()
        if key_lower in HMAC_EXCLUDED_HEADERS:
            continue
        norm[key_lower] = str(v)
    return "&".join(f"{k}={norm[k]}" for k in sorted(norm))


def hmac_head_sign(method: str, sign_path: str, params: Optional[Dict[str, Any]],
                   body: Optional[Dict[str, Any]], headers: Dict[str, Any]) -> str:
    """头签名：HMAC-SHA256("METHOD\\npath\\nparams\\nbody\\nheaders\\n", key).
    
    sign_path 必须以 /yunzhi 开头，如 /yunzhi/api/content/home-popups/init
    body 为 dict 时按 key 升序 k=v 拼接，dict/list 值 JSON 紧凑序列化（与前端 Xu() 一致）。
    """
    def serialize_params(p: Optional[Dict[str, Any]]) -> str:
        if not p:
            return ""
        return "&".join(f"{k}={p[k]}" for k in sorted(p) if p[k] is not None)

    def serialize_body(d: Any) -> str:
        if not d:
            return ""
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                return d
        if not isinstance(d, dict):
            return str(d)
        out = []
        for k in sorted(d.keys()):
            v = d[k]
            if v is None:
                continue
            if isinstance(v, (dict, list)):
                dumped = json.dumps(v, separators=(",", ":"), ensure_ascii=False)
                out.append(f"{k}={dumped}")
            else:
                out.append(f"{k}={v}")
        return "&".join(out)

    raw = (
        f"{(method or 'get').upper()}\n{sign_path}\n{serialize_params(params)}\n"
        f"{serialize_body(body)}\n{canonicalize_headers(headers)}\n"
    )
    return hmac.new(YUNZHI_HMAC_KEY.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()


def build_request_headers(token: str, device_no: str, method: str,
                          api_path: str, body: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """构造完整 HTTP 请求头并注入计算后的 HMAC 头签名"""
    headers = {
        "authorization": token or "",
        "device_type": "3",
        "client_type": "h5",
        "channel_code": YUNZHI_CHANNEL_CODE,
        "version": YUNZHI_VERSION,
        "api_version": "1",
        "device_no": device_no or "a3eef24f4e96d698",
        "accept": "application/json",
        "content-type": "application/json",
        "cache-control": "no-cache",
        "timestamp": str(int(time.time() * 1000)),
        "request_id": generate_request_id(),
    }
    # 头签名对最终 body (业务参数 + timestamp + 体签名 sign) 计算
    headers["sign"] = hmac_head_sign(method, "/yunzhi" + api_path, None, body, headers)
    return headers


# ==================== 脱敏输出辅助函数 ====================

def redact_token(token: Optional[str]) -> str:
    """脱敏打印 Token，保护用户凭据隐私"""
    if not token:
        return "(empty)"
    if len(token) <= 18:
        return token[:3] + "..." + token[-3:]
    return token[:8] + "..." + token[-6:]


def log(msg: str, level: str = "INFO", json_mode: bool = False):
    """控制台日志格式化输出"""
    if json_mode:
        return
    prefix = {
        "INFO": "[\033[34m*\033[0m]",
        "SUCCESS": "[\033[32m+\033[0m]",
        "WARN": "[\033[33m!\033[0m]",
        "ERROR": "[\033[31m-\033[0m]",
    }.get(level, "[*]")
    print(f"{prefix} {msg}", flush=True)


# ==================== 网络请求客户端 ====================

class YunzhiClient:
    """云智手机 API 客户端封装，支持 CDP 与 Direct HTTP 双驱动"""

    def __init__(self, token: str = "", device_no: str = "", cdp_url: str = "",
                 verbose: bool = False, json_mode: bool = False):
        self.token = token
        self.device_no = device_no
        self.cdp_url = cdp_url
        self.verbose = verbose
        self.json_mode = json_mode
        self._page = None
        self._created_new_page = False
        self._browser = None
        self._playwright = None

    async def init(self) -> bool:
        """初始化连接：若指定 CDP 则连入浏览器读取 Token 并准备页面"""
        if self.cdp_url:
            log(f"正在连接 Chrome CDP 实例 ({self.cdp_url})...", "INFO", self.json_mode)
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                log("未检测到 playwright 依赖，无法通过 CDP 连入浏览器 (请先执行: pip install playwright)", "ERROR", self.json_mode)
                return False

            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.connect_over_cdp(self.cdp_url)
                ctx = self._browser.contexts[0] if self._browser.contexts else await self._browser.new_context()

                # 优先寻找已打开的 yunzhi 页面
                target_page = None
                for pg in ctx.pages:
                    if "yunzhi.play.cn" in pg.url or "new-gm.cn" in pg.url:
                        target_page = pg
                        break

                if not target_page:
                    log("未找到已打开的云智标签页，正在新建后台标签页...", "INFO", self.json_mode)
                    target_page = await ctx.new_page()
                    self._created_new_page = True
                    await target_page.goto(YUNZHI_ENTRY_URL, wait_until="commit", timeout=20000)
                    await asyncio.sleep(2.0)

                self._page = target_page

                # 自动提取登录凭据
                creds = await self._page.evaluate(YUNZHI_CREDS_JS)
                if isinstance(creds, dict):
                    extracted_token = creds.get("token") or ""
                    extracted_device = creds.get("deviceNo") or ""
                    if extracted_token and not self.token:
                        self.token = extracted_token
                        log(f"已从浏览器自动提取 Token: {redact_token(self.token)}", "SUCCESS", self.json_mode)
                    if extracted_device and not self.device_no:
                        self.device_no = extracted_device

                if not self.token:
                    log("浏览器中未找到有效的 cloud_phone_token，请确保已在 Chrome 中登录该页面！", "ERROR", self.json_mode)
                    return False
                return True
            except Exception as e:
                log(f"CDP 连接或初始化失败: {e}", "ERROR", self.json_mode)
                return False

        # Direct 模式直接校验传入的 Token
        if not self.token:
            log("未提供 Token 且未配置 CDP！可通过 --token 或 YUNZHI_TOKEN 环境变量提供。", "ERROR", self.json_mode)
            return False
        return True

    async def close(self):
        """释放资源"""
        if self._created_new_page and self._page:
            try:
                await self._page.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass

    async def request(self, method: str, api_path: str,
                      body_params: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
        """统一请求接口：优先走 CDP 页面内 fetch，降级走 Direct HTTP
        
        返回 (data_dict, error_message)，error_message 为空代表成功。
        """
        method = (method or "GET").upper()
        body = None
        if body_params is not None:
            body = dict(body_params)
            body["timestamp"] = int(time.time() * 1000)
            body["sign"] = md5_body_sign(body)

        headers = build_request_headers(self.token, self.device_no, method, api_path, body)
        url = YUNZHI_API_BASE + api_path

        # 模式 1：CDP 页面内 fetch（100% 避开 Edge WAF 503 TLS 检查）
        if self._page is not None:
            payload = {
                "method": method,
                "url": url,
                "headers": headers,
                # Python 预序列化为字符串直传，避免 JS 丢失 > 2^53 大整数精度
                "body": json.dumps(body, separators=(",", ":"), ensure_ascii=False) if body else None,
            }
            try:
                resp = await self._page.evaluate(YUNZHI_FETCH_JS, payload)
            except Exception as e:
                return {}, f"页面内 fetch 异常: {e}"

            if not isinstance(resp, dict):
                return {}, "页面内 fetch 返回空响应"

            # 更新可能刷新的 Token
            new_auth = resp.get("_authorization")
            if new_auth and new_auth != self.token:
                self.token = new_auth

            status = resp.get("_http_status", 0)
            data = resp.get("_data")
            if status != 200:
                return {}, f"HTTP {status} 错误"
            if not isinstance(data, dict):
                return {}, "响应非有效 JSON 格式"

            code = data.get("code")
            if code not in (0, 200):
                msg = data.get("message") or f"业务错误 (code={code})"
                return data, msg
            return data.get("data") or {}, ""

        # 模式 2：Direct HTTP (支持 curl_cffi / urllib)
        return await self._direct_http_request(method, url, headers, body)

    async def _direct_http_request(self, method: str, url: str, headers: Dict[str, str],
                                   body: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], str]:
        """Direct HTTP 模式请求实现"""
        body_bytes = None
        if body is not None:
            body_bytes = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

        # 尝试使用 curl_cffi 模拟 Chrome 120 规避 WAF TLS 指纹审查
        try:
            from curl_cffi.requests import AsyncSession
            try:
                async with AsyncSession(impersonate="chrome120") as s:
                    r = await s.request(method, url, headers=headers, data=body_bytes, timeout=15)
                    if r.status_code == 503:
                        return {}, "WAF 拦截 (HTTP 503): 直连被边缘防火墙 TLS 指纹拦截，请改用 --cdp 模式运行"
                    if r.status_code != 200:
                        return {}, f"HTTP {r.status_code} 错误"

                    # 提取并同步轮换新 Authorization Token
                    new_auth = r.headers.get("authorization")
                    if new_auth and new_auth != self.token:
                        self.token = new_auth

                    try:
                        data = r.json()
                    except Exception:
                        return {}, "响应非有效 JSON"

                    if not isinstance(data, dict):
                        return {}, f"响应非有效 JSON 结构: {str(data)[:60]}"

                    code = data.get("code")
                    if code not in (0, 200):
                        return data, data.get("message") or f"业务错误 (code={code})"

                    res_data = data.get("data")
                    return res_data if isinstance(res_data, dict) else {}, ""
            except Exception as e:
                if self.verbose:
                    log(f"curl_cffi 请求异常 ({e})，正在尝试标准 urllib 兜底...", "WARN", self.json_mode)
        except ImportError:
            pass

        # 标准 urllib 兜底
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()

            def _send():
                with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                    resp_headers = dict(resp.headers)
                    new_auth = resp_headers.get("authorization") or resp_headers.get("Authorization")
                    return resp.read(), new_auth

            res_bytes, new_auth = await loop.run_in_executor(None, _send)
            if new_auth and new_auth != self.token:
                self.token = new_auth

            try:
                data = json.loads(res_bytes.decode("utf-8"))
            except Exception:
                return {}, "响应非有效 JSON"

            if not isinstance(data, dict):
                return {}, f"响应非有效 JSON 结构: {str(data)[:60]}"

            code = data.get("code")
            if code not in (0, 200):
                return data, data.get("message") or f"业务错误 (code={code})"

            res_data = data.get("data")
            return res_data if isinstance(res_data, dict) else {}, ""
        except urllib.error.HTTPError as e:
            if e.code == 503:
                return {}, "WAF 拦截 (HTTP 503): 直连被边缘防火墙拦截！解决方案：使用 --cdp 模式或使用浏览器一键脚本"
            return {}, f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            return {}, f"网络请求失败: {e}"


# ==================== 业务签到与流程编排 ====================

async def run_smoke_test(client: YunzhiClient) -> Dict[str, Any]:
    """运行只读烟测，检查接口与账户健康状态"""
    summary = {
        "status": "FAIL",
        "auth_valid": False,
        "token": redact_token(client.token),
        "popups": [],
        "claimable_popups": 0,
        "benefit_158": None,
        "user_items_count": 0,
        "cloud_devices_count": 0,
        "running_devices_count": 0,
        "member_status": None,
        "details": [],
    }

    # 1. 弹窗探活
    pop_data, pop_err = await client.request("GET", "/api/content/home-popups/init")
    if pop_err:
        summary["details"].append(f"home-popups/init 失败: {pop_err}")
    else:
        summary["auth_valid"] = True
        popups = pop_data.get("popups") or []
        summary["popups"] = popups
        summary["claimable_popups"] = sum(
            1 for p in popups if isinstance(p, dict) and (p.get("canClaim") is True or p.get("state") == "CAN_CLAIM")
        )
        summary["details"].append(f"弹窗接口正常，发现 {len(popups)} 个弹窗，其中 {summary['claimable_popups']} 个可领")

    # 2. 权益查询
    ben_data, ben_err = await client.request("POST", "/api/benefit/user/benefit", {"benefitConfigId": YUNZHI_BENEFIT_ID})
    if ben_err:
        summary["details"].append(f"benefit/user/benefit 失败: {ben_err}")
    else:
        summary["auth_valid"] = True
        user_items = ben_data.get("userItems") or []
        devices = ben_data.get("cloudDevices") or []
        running = [d for d in devices if isinstance(d, dict) and d.get("status") == 2]
        summary["user_items_count"] = len(user_items)
        summary["cloud_devices_count"] = len(devices)
        summary["running_devices_count"] = len(running)
        summary["benefit_158"] = {
            "remainingQuota": ben_data.get("remainingQuota"),
            "userItems": len(user_items),
            "cloudDevices": len(devices),
            "runningDeviceIds": [d.get("vendorResourceId") for d in running if d.get("vendorResourceId")],
        }
        summary["details"].append(
            f"权益 158 正常: 待开通卡片 {len(user_items)} 张, 运行中云机 {len(running)} 台, 剩余配额 {ben_data.get('remainingQuota')}"
        )

    # 3. 会员状态
    mem_data, mem_err = await client.request("GET", "/api/benefit/user/memberStatus")
    if not mem_err and isinstance(mem_data, dict):
        summary["member_status"] = {
            "status": mem_data.get("memberStatus"),
            "expireTime": mem_data.get("memberExpireTime"),
        }
        summary["details"].append(f"会员状态: {mem_data.get('memberStatus')}, 到期时间: {mem_data.get('memberExpireTime')}")

    if summary["auth_valid"] and not pop_err and not ben_err:
        summary["status"] = "OK"

    return summary


async def run_checkin_flow(client: YunzhiClient) -> Dict[str, Any]:
    """执行完整自动化签到与权益开通流程"""
    result = {
        "status": "FAIL",
        "detail": "",
        "token": redact_token(client.token),
        "steps": [],
        "activated_cards": [],
        "new_expire_time": "",
    }

    # Step 1: 每日登录福利弹窗领取
    log("Step 1/4: 检查并领取每日登录福利弹窗...", "INFO", client.json_mode)
    init_data, init_err = await client.request("GET", "/api/content/home-popups/init")
    if init_err:
        result["detail"] = f"弹窗查询失败: {init_err}"
        return result

    popups = init_data.get("popups") or []
    claimable = [
        p for p in popups
        if isinstance(p, dict) and (p.get("canClaim") is True or str(p.get("state") or "") == "CAN_CLAIM")
    ]

    popup_note = "今日弹窗无可领福利"
    if claimable:
        pid = claimable[0].get("popupId")
        log(f"发现可领福利弹窗 (popupId={pid})，正在领取...", "INFO", client.json_mode)
        claim_res, claim_err = await client.request("POST", f"/api/content/home-popups/{pid}/claim")
        if claim_err:
            popup_note = f"弹窗 {pid} 领取异常: {claim_err}"
            log(popup_note, "WARN", client.json_mode)
        else:
            if claim_res.get("claimed") or claim_res.get("success"):
                popup_note = f"弹窗 {pid} 福利卡领取成功 (2天云机空间)"
                log(popup_note, "SUCCESS", client.json_mode)
            else:
                popup_note = f"弹窗 {pid}: {claim_res.get('failReason') or '已领或无需领'}"
                log(popup_note, "INFO", client.json_mode)
    else:
        log(popup_note, "INFO", client.json_mode)
    result["steps"].append({"step": "popup", "note": popup_note})

    # Step 2: 查询待开通权益卡与云机
    log("Step 2/4: 查询待开通云机空间卡 (benefitId=158)...", "INFO", client.json_mode)
    async def fetch_benefit():
        return await client.request("POST", "/api/benefit/user/benefit", {"benefitConfigId": YUNZHI_BENEFIT_ID})

    b_data, b_err = await fetch_benefit()
    if b_err:
        result["detail"] = f"权益卡查询失败: {b_err}"
        return result

    user_items = b_data.get("userItems") or []
    devices = b_data.get("cloudDevices") or []

    # 刚领取弹窗但可能后台异步入账，重试 3 次缓冲
    if not user_items and "领取成功" in popup_note:
        log("权益卡可能异步入账中，正在缓冲查询...", "INFO", client.json_mode)
        for i in range(3):
            await asyncio.sleep(1.5)
            b_data_retry, b_err_retry = await fetch_benefit()
            if not b_err_retry:
                b_data = b_data_retry
                user_items = b_data.get("userItems") or []
                devices = b_data.get("cloudDevices") or devices
                if user_items:
                    break

    # 无待开通权益卡时的结语判定
    if not user_items:
        remaining_quota = b_data.get("remainingQuota")
        if not claimable and remaining_quota == 0:
            result["status"] = "ALREADY"
            result["detail"] = f"{popup_note}; 账户无待开通权益卡，今日配额已全部生效"
            log(result["detail"], "SUCCESS", client.json_mode)
            return result
        result["status"] = "OK"
        result["detail"] = f"{popup_note}; 暂无待开通卡片 (remainingQuota={remaining_quota})"
        log(result["detail"], "INFO", client.json_mode)
        return result

    # 寻找运行中设备
    running_dev = None
    for d in devices:
        if isinstance(d, dict) and d.get("status") == 2:
            running_dev = d
            break
    if not running_dev and devices and isinstance(devices[0], dict):
        running_dev = devices[0]

    if not running_dev or not running_dev.get("vendorResourceId"):
        result["detail"] = f"发现 {len(user_items)} 张待开通卡片，但未找到可用的云机实例！"
        log(result["detail"], "ERROR", client.json_mode)
        return result

    resource_id = str(running_dev.get("vendorResourceId"))
    log(f"目标云机: {resource_id} (待开通卡片: {len(user_items)} 张)", "INFO", client.json_mode)

    # Step 3 & 4: 逐卡开通与轮询确认
    log("Step 3/4: 正在开通权益卡到目标云机...", "INFO", client.json_mode)
    activated = []
    failures = []

    for item in user_items:
        if not isinstance(item, dict):
            continue
        uid = item.get("userItemId")
        if uid is None:
            continue

        log(f"正在开通卡片 userItemId={uid} ...", "INFO", client.json_mode)
        c_res, c_err = await client.request("POST", "/api/benefit/claim", {
            "userItemId": uid,
            "resourceId": resource_id,
        })

        if c_err:
            if any(w in c_err for w in ("已领取", "已开通", "已使用", "重复领取")):
                activated.append(f"卡片 {uid} (已开通)")
            else:
                failures.append(f"卡片 {uid} 开通失败: {c_err}")
            continue

        claim_id = c_res.get("claimId")
        status = c_res.get("status")
        if not claim_id:
            failures.append(f"卡片 {uid} 未返回 claimId")
            continue

        # 轮询状态
        log(f"已提交开通任务 claimId={claim_id}，正在轮询生效状态...", "INFO", client.json_mode)
        done = False
        for _ in range(10):
            if status == 1:
                activated.append(f"卡片 {uid} 开通成功")
                done = True
                break
            if status == 2:
                failures.append(f"卡片 {uid} 异步失败: {c_res.get('errorMsg') or '未知错误'}")
                done = True
                break
            await asyncio.sleep(2.0)
            ps_res, ps_err = await client.request("POST", "/api/benefit/claim/status", {"claimId": claim_id})
            if ps_err:
                failures.append(f"轮询 claimId={claim_id} 出错: {ps_err}")
                done = True
                break
            status = ps_res.get("status")
            c_res = ps_res

        if not done:
            failures.append(f"卡片 {uid} (claimId={claim_id}) 轮询超时")

    result["activated_cards"] = activated
    result["failures"] = failures

    # Step 4: 复查有效期与剩余配额
    log("Step 4/4: 复查最终云机有效期...", "INFO", client.json_mode)
    try:
        b_data2, _ = await fetch_benefit()
        for d in (b_data2.get("cloudDevices") or []):
            if isinstance(d, dict) and d.get("expireTime"):
                result["new_expire_time"] = str(d.get("expireTime"))
                break
    except Exception:
        pass

    if activated:
        if all("(已开通)" in a for a in activated) and not failures and "领取成功" not in popup_note:
            result["status"] = "ALREADY"
        else:
            result["status"] = "OK"
        detail_parts = [popup_note] + activated
        if result["new_expire_time"]:
            detail_parts.append(f"云机有效期更新至: {result['new_expire_time']}")
        if failures:
            detail_parts.append("部分开通异常: " + "; ".join(failures))
        result["detail"] = " | ".join(detail_parts)
        log_type = "SUCCESS" if result["status"] in ("OK", "ALREADY") else "WARN"
        prefix = "今日已在保！" if result["status"] == "ALREADY" else "签到成功！"
        log(f"{prefix}{result['detail']}", log_type, client.json_mode)
    elif failures:
        result["detail"] = "; ".join(failures)
        log(f"签到失败: {result['detail']}", "ERROR", client.json_mode)
    else:
        result["status"] = "ALREADY"
        result["detail"] = f"{popup_note}; 今日无新卡可开通"
        log(result["detail"], "INFO", client.json_mode)

    return result


# ==================== CLI 命令行入口 ====================

def parse_args():
    parser = argparse.ArgumentParser(
        description="云智手机 (yunzhi.play.cn) 自动化签到与云机空间权益领取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cdp",
        default=os.environ.get("CDP_HTTP", ""),
        help="Chrome DevTools Protocol 地址 (例如 http://127.0.0.1:9222，推荐首选)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("YUNZHI_TOKEN", ""),
        help="云智手机 JWT Token (若未提供 CDP 则必须提供此项)",
    )
    parser.add_argument(
        "--device-no",
        default=os.environ.get("YUNZHI_DEVICE_NO", ""),
        help="设备标识号 (可选，默认自动从浏览器提取或生成)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="只读烟测模式：仅检查登录态与配额，不执行任何消耗性操作",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出最终执行结果",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="打印详细调试日志",
    )
    return parser.parse_args()


async def main_async():
    args = parse_args()

    client = YunzhiClient(
        token=args.token.strip(),
        device_no=args.device_no.strip(),
        cdp_url=args.cdp.strip(),
        verbose=args.verbose,
        json_mode=args.json,
    )

    try:
        ok = await client.init()
        if not ok:
            err_res = {"status": "FAIL", "detail": "客户端初始化或凭据提取失败"}
            if args.json:
                print(json.dumps(err_res, ensure_ascii=False, indent=2))
            return 1

        if args.smoke:
            log("=== 启动云智手机只读状态烟测 ===", "INFO", args.json)
            smoke_res = await run_smoke_test(client)
            if args.json:
                print(json.dumps(smoke_res, ensure_ascii=False, indent=2))
            else:
                for line in smoke_res.get("details", []):
                    log(f"  {line}", "INFO")
                log(f"烟测结果: {smoke_res['status']}", "SUCCESS" if smoke_res["status"] == "OK" else "ERROR")
            return 0 if smoke_res["status"] == "OK" else 1

        log("=== 启动云智手机每日自动化签到 ===", "INFO", args.json)
        result = await run_checkin_flow(client)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in ("OK", "ALREADY") else 1

    finally:
        await client.close()


def main():
    try:
        code = asyncio.run(main_async())
        sys.exit(code)
    except KeyboardInterrupt:
        print("\n[!] 操作已由用户手动中断")
        sys.exit(130)


if __name__ == "__main__":
    main()
