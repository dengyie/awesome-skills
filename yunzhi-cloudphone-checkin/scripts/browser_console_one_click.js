/**
 * 云智手机 (yunzhi.play.cn) 浏览器控制台一键全自动签到与权益领取脚本
 * 
 * 【使用方法】
 * 1. 在电脑浏览器打开并登录云智手机页面：
 *    https://yunzhi.play.cn/ai/?channel_code=00000042
 * 2. 按 F12 (或 Command+Option+I / 鼠标右键 -> 检查) 打开开发者工具，切换到 "Console" (控制台) 标签页。
 * 3. 复制本文件的全部内容，粘贴到控制台并回车运行即可！
 * 
 * 【特点】
 * - 纯前端原生运行，零安装依赖，无需配置 Python 或任何环境。
 * - 原生运行在当前页面上下文，天然具备完美浏览器指纹，零 503 WAF 拦截风险。
 * - 纯本地执行，Token 凭据绝不上报第三方。
 */

(async function yunzhiOneClickCheckin() {
  const STYLE_TITLE = "color: #00e5a3; font-weight: bold; font-size: 14px;";
  const STYLE_INFO = "color: #38bdf8; font-size: 12px;";
  const STYLE_SUCCESS = "color: #22c55e; font-weight: bold; font-size: 12px;";
  const STYLE_WARN = "color: #f59e0b; font-size: 12px;";
  const STYLE_ERROR = "color: #ef4444; font-weight: bold; font-size: 12px;";

  console.log("%c=================================================", STYLE_TITLE);
  console.log("%c🚀 云智手机一键自动打卡与 2 天云机空间领取开始...", STYLE_TITLE);
  console.log("%c=================================================", STYLE_TITLE);

  // 1. 读取当前登录凭据
  let token = localStorage.getItem("cloud_phone_token") || "";
  if (!token) {
    const m = document.cookie.match(/(?:^|; )CG_CLINET_USER_TOKEN_YUN=([^;]*)/);
    if (m) token = decodeURIComponent(m[1]);
  }
  const deviceNo = localStorage.getItem("cloud_phone_device_no") || "a3eef24f4e96d698";

  if (!token) {
    console.log("%c❌ 未检测到登录凭据！请先在当前页面完成登录后再次运行本脚本。", STYLE_ERROR);
    return;
  }
  console.log(`%c[1/4] 凭据读取成功: ${token.slice(0, 8)}...${token.slice(-6)}`, STYLE_INFO);

  // 常量与秘钥定义
  const API_BASE = "https://yunzhi.new-gm.cn/yunzhi";
  const SIGN_SALT = "7f9e2d08c1b5a3709e4f6d2a8c0e1b3f";
  const HMAC_KEY = "8822FF81B6623e6f338d6F2A7F49DA83";
  const CHANNEL_CODE = "00000042";
  const VERSION = "10310";
  const BENEFIT_ID = "158";

  // 轻量纯 JS MD5 实现
  function md5(str) {
    function safeAdd(x, y) {
      const lsw = (x & 0xffff) + (y & 0xffff);
      const msw = (x >> 16) + (y >> 16) + (lsw >> 16);
      return (msw << 16) | (lsw & 0xffff);
    }
    function bitRol(num, cnt) {
      return (num << cnt) | (num >>> (32 - cnt));
    }
    function md5cmn(q, a, b, x, s, t) {
      return safeAdd(bitRol(safeAdd(safeAdd(a, q), safeAdd(x, t)), s), b);
    }
    function md5ff(a, b, c, d, x, s, t) {
      return md5cmn((b & c) | (~b & d), a, b, x, s, t);
    }
    function md5gg(a, b, c, d, x, s, t) {
      return md5cmn((b & d) | (c & ~d), a, b, x, s, t);
    }
    function md5hh(a, b, c, d, x, s, t) {
      return md5cmn(b ^ c ^ d, a, b, x, s, t);
    }
    function md5ii(a, b, c, d, x, s, t) {
      return md5cmn(c ^ (b | ~d), a, b, x, s, t);
    }
    function binlMD5(x, len) {
      x[len >> 5] |= 0x80 << (len % 32);
      x[(((len + 64) >>> 9) << 4) + 14] = len;
      let a = 1732584193, b = -271733879, c = -1732584194, d = 271733878;
      for (let i = 0; i < x.length; i += 16) {
        const olda = a, oldb = b, oldc = c, oldd = d;
        a = md5ff(a, b, c, d, x[i], 7, -680876936);
        d = md5ff(d, a, b, c, x[i + 1], 12, -389564586);
        c = md5ff(c, d, a, b, x[i + 2], 17, 606105819);
        b = md5ff(b, c, d, a, x[i + 3], 22, -1044525330);
        a = md5ff(a, b, c, d, x[i + 4], 7, -176418897);
        d = md5ff(d, a, b, c, x[i + 5], 12, 1200080426);
        c = md5ff(c, d, a, b, x[i + 6], 17, -1473231341);
        b = md5ff(b, c, d, a, x[i + 7], 22, -45705983);
        a = md5ff(a, b, c, d, x[i + 8], 7, 1770035416);
        d = md5ff(d, a, b, c, x[i + 9], 12, -1958414417);
        c = md5ff(c, d, a, b, x[i + 10], 17, -42063);
        b = md5ff(b, c, d, a, x[i + 11], 22, -1990404162);
        a = md5ff(a, b, c, d, x[i + 12], 7, 1804603682);
        d = md5ff(d, a, b, c, x[i + 13], 12, -40341101);
        c = md5ff(c, d, a, b, x[i + 14], 17, -1502002290);
        b = md5ff(b, c, d, a, x[i + 15], 22, 1236535329);

        a = md5gg(a, b, c, d, x[i + 1], 5, -165796510);
        d = md5gg(d, a, b, c, x[i + 6], 9, -1069501632);
        c = md5gg(c, d, a, b, x[i + 11], 14, 643717713);
        b = md5gg(b, c, d, a, x[i], 20, -373897302);
        a = md5gg(a, b, c, d, x[i + 5], 5, -701558691);
        d = md5gg(d, a, b, c, x[i + 10], 9, 38016083);
        c = md5gg(c, d, a, b, x[i + 15], 14, -660478335);
        b = md5gg(b, c, d, a, x[i + 4], 20, -405537848);
        a = md5gg(a, b, c, d, x[i + 9], 5, 568446438);
        d = md5gg(d, a, b, c, x[i + 14], 9, -1019803690);
        c = md5gg(c, d, a, b, x[i + 3], 14, -187363961);
        b = md5gg(b, c, d, a, x[i + 8], 20, 1163531501);
        a = md5gg(a, b, c, d, x[i + 13], 5, -1444681467);
        d = md5gg(d, a, b, c, x[i + 2], 9, -51403784);
        c = md5gg(c, d, a, b, x[i + 7], 14, 1735328473);
        b = md5gg(b, c, d, a, x[i + 12], 20, -1926607734);

        a = md5hh(a, b, c, d, x[i + 5], 4, -378558);
        d = md5hh(d, a, b, c, x[i + 8], 11, -2022574463);
        c = md5hh(c, d, a, b, x[i + 11], 16, 1839030562);
        b = md5hh(b, c, d, a, x[i + 14], 23, -35309556);
        a = md5hh(a, b, c, d, x[i + 1], 4, -1530992060);
        d = md5hh(d, a, b, c, x[i + 4], 11, 1272893353);
        c = md5hh(c, d, a, b, x[i + 7], 16, -155497632);
        b = md5hh(b, c, d, a, x[i + 10], 23, -1094730640);
        a = md5hh(a, b, c, d, x[i + 13], 4, 681279174);
        d = md5hh(d, a, b, c, x[i], 11, -358537222);
        c = md5hh(c, d, a, b, x[i + 3], 16, -722521979);
        b = md5hh(b, c, d, a, x[i + 6], 23, 76029189);
        a = md5hh(a, b, c, d, x[i + 9], 4, -640364487);
        d = md5hh(d, a, b, c, x[i + 12], 11, -421815835);
        c = md5hh(c, d, a, b, x[i + 15], 16, 530742520);
        b = md5hh(b, c, d, a, x[i + 2], 23, -995338651);

        a = md5ii(a, b, c, d, x[i], 6, -198630844);
        d = md5ii(d, a, b, c, x[i + 7], 10, 1126891415);
        c = md5ii(c, d, a, b, x[i + 14], 15, -1416354905);
        b = md5ii(b, c, d, a, x[i + 5], 21, -57434055);
        a = md5ii(a, b, c, d, x[i + 12], 6, 1700485571);
        d = md5ii(d, a, b, c, x[i + 3], 10, -1894986606);
        c = md5ii(c, d, a, b, x[i + 10], 15, -1051523);
        b = md5ii(b, c, d, a, x[i + 1], 21, -2054922799);
        a = md5ii(a, b, c, d, x[i + 8], 6, 1873313359);
        d = md5ii(d, a, b, c, x[i + 15], 10, -30611744);
        c = md5ii(c, d, a, b, x[i + 6], 15, -1560198380);
        b = md5ii(b, c, d, a, x[i + 13], 21, 1309151649);
        a = md5ii(a, b, c, d, x[i + 4], 6, -145523070);
        d = md5ii(d, a, b, c, x[i + 11], 10, -1120210379);
        c = md5ii(c, d, a, b, x[i + 2], 15, 718787259);
        b = md5ii(b, c, d, a, x[i + 9], 21, -343485551);

        a = safeAdd(a, olda);
        b = safeAdd(b, oldb);
        c = safeAdd(c, oldc);
        d = safeAdd(d, oldd);
      }
      return [a, b, c, d];
    }
    function binl2rstr(input) {
      let output = "";
      for (let i = 0; i < input.length * 32; i += 8) {
        output += String.fromCharCode((input[i >> 5] >>> (i % 32)) & 0xff);
      }
      return output;
    }
    function rstr2binl(input) {
      const output = [];
      for (let i = 0; i < input.length * 8; i += 8) {
        output[i >> 5] |= (input.charCodeAt(i / 8) & 0xff) << (i % 32);
      }
      return output;
    }
    function rstr2hex(input) {
      const hexTab = "0123456789abcdef";
      let output = "";
      for (let i = 0; i < input.length; i++) {
        const x = input.charCodeAt(i);
        output += hexTab.charAt((x >>> 4) & 0x0f) + hexTab.charAt(x & 0x0f);
      }
      return output;
    }
    const utf8 = unescape(encodeURIComponent(str));
    return rstr2hex(binl2rstr(binlMD5(rstr2binl(utf8), utf8.length * 8)));
  }

  // Web Crypto HMAC-SHA256
  async function hmacSha256(keyStr, messageStr) {
    const enc = new TextEncoder();
    const keyData = enc.encode(keyStr);
    const msgData = enc.encode(messageStr);
    const key = await crypto.subtle.importKey(
      "raw", keyData, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
    );
    const signature = await crypto.subtle.sign("HMAC", key, msgData);
    return Array.from(new Uint8Array(signature))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }

  function generateRequestId() {
    return "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  // 接口请求包装
  async function api(method, apiPath, bodyParams) {
    let body = null;
    if (bodyParams) {
      body = { ...bodyParams, timestamp: Date.now() };
      // 体签名
      const sortedKeys = Object.keys(body).filter((k) => k !== "sign" && body[k] !== null).sort();
      const qs = sortedKeys.map((k) => `${k}=${body[k]}`).join("&");
      body.sign = md5(qs + SIGN_SALT);
    }

    const headers = {
      authorization: token,
      device_type: "3",
      client_type: "h5",
      channel_code: CHANNEL_CODE,
      version: VERSION,
      api_version: "1",
      device_no: deviceNo,
      accept: "application/json",
      "content-type": "application/json",
      "cache-control": "no-cache",
      timestamp: String(Date.now()),
      request_id: generateRequestId(),
    };

    // 头规范化
    const excluded = new Set([
      "content-length", "host", "connection", "accept-encoding", "user-agent",
      "sign", "content-type", "accept", "device_code", "model", "api_level", "cache-control"
    ]);
    const normHeaders = Object.keys(headers)
      .filter((k) => !excluded.has(k.toLowerCase()) && headers[k] !== null)
      .sort()
      .map((k) => `${k.toLowerCase()}=${headers[k]}`)
      .join("&");

    // 序列化 body 供头签名
    let bodyStr = "";
    if (body) {
      bodyStr = Object.keys(body)
        .sort()
        .filter((k) => body[k] !== null)
        .map((k) => {
          const v = body[k];
          return `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`;
        })
        .join("&");
    }

    const rawToSign = `${method.toUpperCase()}\n/yunzhi${apiPath}\n\n${bodyStr}\n${normHeaders}\n`;
    headers.sign = await hmacSha256(HMAC_KEY, rawToSign);

    const resp = await fetch(API_BASE + apiPath, {
      method: method.toUpperCase(),
      headers: headers,
      body: body ? JSON.stringify(body) : null,
    });

    const newAuth = resp.headers.get("authorization");
    if (newAuth) token = newAuth;

    const resJson = await resp.json();
    return resJson;
  }

  try {
    // 2. 检查每日登录福利弹窗
    console.log("%c[2/4] 检查每日登录弹窗福利...", STYLE_INFO);
    const popRes = await api("GET", "/api/content/home-popups/init");
    const popups = (popRes.data && popRes.data.popups) || [];
    const claimable = popups.find((p) => p.canClaim === true || p.state === "CAN_CLAIM");

    if (claimable && claimable.popupId) {
      console.log(`%c发现可领福利 (popupId=${claimable.popupId})，正在领取...`, STYLE_INFO);
      const cRes = await api("POST", `/api/content/home-popups/${claimable.popupId}/claim`);
      if (cRes.code === 0 || cRes.code === 200) {
        console.log("%c✅ 每日登录弹窗福利领取成功 (2 天云机空间卡)！", STYLE_SUCCESS);
      } else {
        console.log(`%c⚠️ 弹窗领取提示: ${cRes.message || "未能成功领取"}`, STYLE_WARN);
      }
      await new Promise((r) => setTimeout(r, 1500));
    } else {
      console.log("%cℹ️ 今日弹窗福利已领或无可领项。", STYLE_INFO);
    }

    // 3. 查询待开通权益卡与云机
    console.log("%c[3/4] 正在查询待生效卡片与云机设备...", STYLE_INFO);
    let benRes = await api("POST", "/api/benefit/user/benefit", { benefitConfigId: BENEFIT_ID });
    let items = (benRes.data && benRes.data.userItems) || [];
    let devices = (benRes.data && benRes.data.cloudDevices) || [];

    // 若刚领了弹窗，稍等重试一次刷新入账
    if (items.length === 0 && claimable) {
      await new Promise((r) => setTimeout(r, 2000));
      benRes = await api("POST", "/api/benefit/user/benefit", { benefitConfigId: BENEFIT_ID });
      items = (benRes.data && benRes.data.userItems) || [];
      devices = (benRes.data && benRes.data.cloudDevices) || [];
    }

    if (items.length === 0) {
      console.log(`%c🎉 当前账户暂无待开通权益卡 (剩余配额: ${benRes.data ? benRes.data.remainingQuota : 0})，说明今日权益已全部在保！`, STYLE_SUCCESS);
      return;
    }

    const runningDevice = devices.find((d) => d.status === 2) || devices[0];
    if (!runningDevice || !runningDevice.vendorResourceId) {
      console.log("%c❌ 发现待开通卡片，但未查询到可用云机！", STYLE_ERROR);
      return;
    }

    const resourceId = runningDevice.vendorResourceId;
    console.log(`%c[4/4] 目标云机: ${resourceId}，待开通卡片数量: ${items.length} 张，正在逐张生效...`, STYLE_INFO);

    for (const item of items) {
      console.log(`%c正在为云机开通卡片 ${item.userItemId}...`, STYLE_INFO);
      const claimRes = await api("POST", "/api/benefit/claim", {
        userItemId: item.userItemId,
        resourceId: resourceId,
      });

      if (claimRes.code !== 0 && claimRes.code !== 200) {
        console.log(`%c⚠️ 卡片开通响应: ${claimRes.message}`, STYLE_WARN);
        continue;
      }

      const claimId = claimRes.data && claimRes.data.claimId;
      if (!claimId) continue;

      // 轮询状态
      let pollStatus = claimRes.data.status;
      for (let i = 0; i < 10; i++) {
        if (pollStatus === 1) {
          console.log(`%c✅ 卡片 ${item.userItemId} 成功续期到云机！`, STYLE_SUCCESS);
          break;
        }
        if (pollStatus === 2) {
          console.log(`%c❌ 卡片 ${item.userItemId} 激活失败: ${claimRes.data.errorMsg || ""}`, STYLE_ERROR);
          break;
        }
        await new Promise((r) => setTimeout(r, 2000));
        const statusRes = await api("POST", "/api/benefit/claim/status", { claimId });
        pollStatus = statusRes.data && statusRes.data.status;
      }
    }

    // 最终复查有效期
    const finalRes = await api("POST", "/api/benefit/user/benefit", { benefitConfigId: BENEFIT_ID });
    const finalDevs = (finalRes.data && finalRes.data.cloudDevices) || [];
    const activeDev = finalDevs.find((d) => d.vendorResourceId === resourceId);
    if (activeDev && activeDev.expireTime) {
      console.log("%c=================================================", STYLE_TITLE);
      console.log(`%c🎉 全部流程完成！云机最新有效期至: ${activeDev.expireTime}`, STYLE_TITLE);
      console.log("%c=================================================", STYLE_TITLE);
    } else {
      console.log("%c🎉 打卡流程执行完毕！", STYLE_SUCCESS);
    }
  } catch (err) {
    console.log(`%c❌ 执行过程中发生异常: ${err.message}`, STYLE_ERROR);
  }
})();
