# 云智手机 (yunzhi.play.cn) 协议逆向与双签名权威参考手册

本文档记录云智手机（天翼/爱游戏平台）云机空间福利签到流程的完整逆向分析结果、双签名计算公式、HTTP 头规范化算法以及全部核心 RPC 接口定义。

---

## 1. 架构与认证模型

- **业务入口**: `https://yunzhi.play.cn/ai/?channel_code=00000042`
- **API 基础域名**: `https://yunzhi.new-gm.cn/yunzhi`
- **目标权益**: 云机空间服务（新开 2 天体验卡），`benefitConfigId = "158"`
- **认证 Token**:
  - 本质为标准 JWT。
  - 持久化位置：网页端 `localStorage.getItem("cloud_phone_token")`。
  - Cookie 镜像：`CG_CLINET_USER_TOKEN_YUN`（作用域 `.play.cn` / `.new-gm.cn`）。
  - 设备号：`localStorage.getItem("cloud_phone_device_no")`（缺省时使用 16 位小写十六进制字符串）。
- **请求头鉴权**: 请求头中以 `authorization: <token>` 明文发送（无 Bearer 前缀）。

---

## 2. 双签名体系（Dual-Signature Architecture）

云智手机的前端（基于 axios 封装的 RPC 客户端）采用**双层加签防御体系**：
1. **第一层：Body MD5 业务体签名**（嵌入在 POST 请求体中的 `sign` 字段）。
2. **第二层：Header HMAC-SHA256 通信头签名**（放在 HTTP 请求头中的 `sign` 字段）。

加签执行的时序**非常关键**：必须先拼装业务参数并计算出 Body MD5 签名，将其写入请求体后，再对包含体签名的「最终请求体」计算 Header HMAC-SHA256 签名。

```
[原始参数] 
   │
   ├─► 注入时间戳: body.timestamp = Date.now()
   ├─► 排除 sign，字典序排序拼接 k=v&... + MD5盐
   ├─► 计算 MD5: body.sign = md5(...)
   │
   ▼
[最终请求体 (含 body.sign)] 
   │
   ├─► 规范化 Header（转小写、过滤 Qu 排除表、排序）
   ├─► 组装待签字符串: METHOD + '\n' + PATH + '\n' + PARAMS + '\n' + BODY + '\n' + HEADERS + '\n'
   ├─► 计算 HMAC-SHA256: headers.sign = hmac(...)
   │
   ▼
[发送 HTTP 请求]
```

### 2.1 Body MD5 签名算法

- **盐值 (Salt)**: `7f9e2d08c1b5a3709e4f6d2a8c0e1b3f`
- **规则**:
  1. 剔除 `sign` 键以及值为 `null` / `undefined` 的键。
  2. 将剩余键按 ASCII 升序排列。
  3. 以 `k=v` 形式拼接，用 `&` 连接。
  4. 末尾直接拼接盐值（无 `&`）。
  5. 计算标准的 32 位小写 MD5 哈希。

**Python 实现**:
```python
def md5_body_sign(params: dict) -> str:
    items = {k: v for k, v in (params or {}).items() if k != "sign" and v is not None}
    qs = "&".join(f"{k}={items[k]}" for k in sorted(items))
    return hashlib.md5((qs + "7f9e2d08c1b5a3709e4f6d2a8c0e1b3f").encode("utf-8")).hexdigest()
```

### 2.2 Header HMAC-SHA256 签名算法

- **秘钥 (Secret Key)**: `8822FF81B6623e6f338d6F2A7F49DA83`
- **签名路径 (sign_path)**: 必须保留 `/yunzhi` 前缀（例如 `/yunzhi/api/content/home-popups/init`）。
- **待签名原始串 (Raw Payload)**: 由 5 个字段以换行符 `\n` 连接，末尾**必须包含换行符 `\n`**：
  ```
  {METHOD}\n
  {SIGN_PATH}\n
  {SERIALIZED_QUERY_PARAMS}\n
  {SERIALIZED_BODY}\n
  {CANONICAL_HEADERS}\n
  ```

#### 2.2.1 头规范化过滤规则 (Canonical Headers)
排除列表（前端代码中的 `Qu` 排除表，不区分大小写）：
- `content-length`
- `host`
- `connection`
- `accept-encoding`
- `user-agent`
- `sign` (注意：请求头本身的 sign 不参与计算)
- `content-type`
- `accept`
- `device_code`
- `model`
- `api_level`
- `cache-control`

剩余头统一转换为**小写**，按键名升序排列，拼接为 `k=v&...`。常见参与签名的头包括：`api_version`, `authorization`, `channel_code`, `client_type`, `device_no`, `device_type`, `request_id`, `timestamp`, `version`。

#### 2.2.2 请求体序列化规则 (Serialized Body)
- 若 Body 为空或 GET 请求，该行为空字符串 `""`。
- 若 Body 为字典/对象，按键升序排列。
- 标量值直接转字符串，对象或数组必须以紧凑 JSON 格式（`separators=(',', ':')`，即无多余空格）序列化，然后以 `k=v&...` 形式拼接。

---

## 3. 完整业务接口定义

### 3.1 查询首页弹窗 (每日登录福利)
- **Method**: `GET`
- **Path**: `/api/content/home-popups/init`
- **请求头**: 包含签名头
- **响应示例**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "popups": [
        {
          "popupId": 1024,
          "title": "今日登录福利",
          "canClaim": true,
          "state": "CAN_CLAIM"
        }
      ]
    }
  }
  ```

### 3.2 领取首页弹窗福利
- **Method**: `POST`
- **Path**: `/api/content/home-popups/{popupId}/claim`
- **请求体**: 空或 `{}`
- **响应示例**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "claimed": true,
      "success": true
    }
  }
  ```

### 3.3 查询用户权益与云机设备
- **Method**: `POST`
- **Path**: `/api/benefit/user/benefit`
- **请求体**:
  ```json
  {
    "benefitConfigId": "158"
  }
  ```
  *(发送时自动注入 timestamp 与 sign)*
- **响应关键字段**:
  - `data.userItems`: 待生效的卡片列表，每项包含 `userItemId`（注意：这是超大长整数，JS 需注意精度）。
  - `data.cloudDevices`: 关联的云机列表，每项包含 `vendorResourceId`、`status`（`2` 代表运行中）与 `expireTime`。
  - `data.remainingQuota`: 剩余权益配额。

### 3.4 绑定权益卡到指定云机
- **Method**: `POST`
- **Path**: `/api/benefit/claim`
- **请求体**:
  ```json
  {
    "userItemId": 355236345335936,
    "resourceId": "D0026092223823038"
  }
  ```
- **响应关键字段**:
  - `data.claimId`: 异步开通任务 ID。
  - `data.status`: `0` 初始/处理中，`1` 成功，`2` 失败。

### 3.5 轮询权益开通生效状态
- **Method**: `POST`
- **Path**: `/api/benefit/claim/status`
- **请求体**:
  ```json
  {
    "claimId": 2720635
  }
  ```
- **响应关键字段**:
  - `data.status`: `1` 成功，`2` 失败，`0` 仍需继续轮询（建议间隔 1.5 ~ 2 秒）。
  - `data.errorMsg`: 失败时的错误信息。

---

## 4. 逆向验证向量 (Test Vectors)

用于离线单元测试与第三方实现的逐字节对齐：

### 4.1 MD5 签名验证向量
1. 向量 1:
   - 输入: `{"benefitConfigId": "158", "timestamp": "1790794831629"}`
   - 预期: `2164c5c88db4005310250a27f3b7807e`
2. 向量 2:
   - 输入: `{"userItemId": 355236345335936, "timestamp": "1790794843383", "resourceId": "D0026092223823038"}`
   - 预期: `2536063923750f79cd4677a1f64460b9`
3. 向量 3:
   - 输入: `{"claimId": 2720635, "timestamp": "1790794845048"}`
   - 预期: `4b0d3010875a47dcda38b1f80861f79a`

### 4.2 HMAC-SHA256 头签名验证向量
- Method: `GET`
- Path: `/yunzhi/api/content/home-popups/init`
- Headers:
  ```json
  {
    "authorization": "TEST_TOKEN_FAKE_123",
    "device_type": "3",
    "client_type": "h5",
    "channel_code": "00000042",
    "version": "10310",
    "api_version": "1",
    "device_no": "a3eef24f4e96d698",
    "timestamp": "1790794811525",
    "request_id": "5d67f86522734bceb951d058e3a7efed",
    "accept": "application/json",
    "content-type": "application/json",
    "cache-control": "no-cache"
  }
  ```
- 预期签名: `2ec6f56786c4c0b1b62a517931e98a038b30ae2b6a0f10e429708c14e4695b00`
