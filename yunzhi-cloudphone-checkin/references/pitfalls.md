# 云智手机 (yunzhi.play.cn) 签到排障与避坑权威指南

本指南汇集了云智手机签到逆向与多端实机运行过程中踩过的**全部真实问题、根因剖析与标准解决方案**。向他人分享本脚本或排查异常时，请优先参考本文档。

---

## 1. 边缘 WAF HTTP 503 拦截与 TLS 指纹（最常见问题）

### 现象
直接使用 Python `requests`、`urllib.request` 或普通 `curl` 请求 `/api/content/home-popups/init` 等接口时，服务器直接返回 `HTTP 503 Service Temporarily Unavailable`，没有任何业务 JSON 返回。

### 根因分析
云智手机网关（域名 `yunzhi.new-gm.cn`）前端挂载了边缘安全网关/Cloudflare 类型的 WAF：
1. WAF 针对 `/api/content/*` 路由开启了严格的 **TLS Client Hello 指纹识别**（JA3 / JA4 指纹）。
2. Python 的 `ssl` / `urllib` 使用的标准 OpenSSL TLS 握手特征（支持的 Cipher Suites、Extensions 顺序）被识别为非浏览器行为，在握手阶段即被阻断，返回 HTTP 503。

### 解决方案（按推荐顺序）
- **方案 A（最佳推荐）：CDP 模式**
  使用 Chrome DevTools Protocol（`python3 yunzhi_checkin.py --cdp http://127.0.0.1:9222`）运行。脚本直接在真实 Chrome 页面内部执行 `fetch()`，请求发自真实浏览器内核，TLS 指纹 100% 真实，完全免疫任何 WAF 拦截。
- **方案 B：浏览器控制台一键脚本**
  直接打开 `scripts/browser_console_one_click.js`，在当前页面的 F12 控制台粘贴运行。适合非技术用户或没有 Python 环境的朋友。
- **方案 C：启用 `curl_cffi` 模拟**
  在 Python 环境中执行 `pip install curl_cffi`。本项目的 `yunzhi_checkin.py` 内部已内置 `curl_cffi` 检测，一旦检测到会自动开启 `impersonate="chrome120"`，无缝模拟 Chrome 指纹直连。

---

## 2. 弹窗领取成功但卡片「延迟入账」问题

### 现象
`home-popups/{id}/claim` 明确返回成功（`claimed: true`），但紧接着调用 `benefit/user/benefit` 查询待开通卡片时，`userItems` 数组却为空。

### 根因分析
云智手机服务端的业务架构中，弹窗领券与卡券入库走的是**异步消息队列**（例如 RabbitMQ / Kafka）：
1. 领券接口向队列投递发卡任务后立即向前端返回 HTTP 200。
2. 权益账户子系统消费队列并插入 `userItems` 表通常存在 500ms ~ 1500ms 的入账延迟。
3. 若签到脚本在领券后立即同步查询，极易读到「未入账」的中间态，导致卡片未能被绑定至云机。

### 规避方案
在代码中实现缓冲轮询：
- 一旦检测到当日领取了弹窗福利，在查询 `user_benefit` 时自动等待 1.5 ~ 2 秒。
- 若 `userItems` 为空，自动重试 2 ~ 3 次，直至卡片成功入账后再执行开通。

---

## 3. JavaScript 64 位大整数精度丢失问题

### 现象
在部分前端环境或 Node.js 中调用开通接口时，接口报错 `卡片不存在` 或 `userItemId 无效`。

### 根因分析
云智手机数据库中的 `userItemId` 为 15~16 位的全局雪花算法 ID（例如 `355236345335936`）。
- 在 JavaScript 中，超过 `Number.MAX_SAFE_INTEGER` (`9007199254740991`，约 16 位) 的整型数值在反序列化或参与计算时，末尾数字会被截断或进位。
- 若直接在 Python Playwright `evaluate(js, dict_object)` 中传递 Python 对象，Playwright 在跨进程 IPC 转换为 JS Object 时可能引发整型失真。

### 解决方案
- 在 Python 端将包含 `userItemId` 的请求体预先序列化为 JSON 字符串（`json.dumps(...)`），以字符串形式直接传入浏览器的 `fetch(url, { body: str })`，彻底绕过 JS 对象的整型转换。

---

## 4. 签名拼接易错细节速查

| 细节项 | 正确做法 | 错误示范（会导致 400 签名错误） |
|---|---|---|
| **待签串末尾换行** | 待签串必须以 `\n` 结尾（共 5 个换行） | 仅用 `\n`.join() 导致末尾缺少 `\n` |
| **路径前缀** | 必须补齐 `/yunzhi`（如 `/yunzhi/api/...`） | 直接写 `/api/...` |
| **HTTP Method 大小写** | 必须全部转为**大写**（`GET`、`POST`） | 使用小写 `get` / `post` |
| **Header 排序与小写** | 键名统一**小写**并按 ASCII 升序排列 | 保留大写驼峰 `Authorization` 或无序 |
| **签名排除头** | 请求头自身的 `sign` **绝对不能**进入规范化头 | 把计算出的 `sign` 又作为输入参与计算 |
| **加签先后时序** | **先算 Body MD5**，填入 body 后**再算 Header HMAC** | 先算 Header HMAC 后算 Body MD5 |

---

## 5. 多云机目标设备选择逻辑

### 现象
多台云机用户打卡后，权益卡被开通到了已停用或已过期的云机上，导致正在使用的云机未能续期。

### 根因分析
接口返回的 `cloudDevices` 列表中包含该用户账户下的所有历史云机：
- `status = 1`: 初始化中 / 准备中
- `status = 2`: **运行中 (Active)**
- `status = 3`: 已关机 / 冻结
- `status = 4`: 已释放 / 过期

### 解决方案
设备选择器必须遵循优先级排序：
1. 优先遍历查找 `status == 2` 且带有有效 `vendorResourceId` 的云机。
2. 若无 `status == 2` 设备，再退化选择第一台设备。
3. 严禁无脑选择索引 `[0]`。
