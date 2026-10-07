# Phone-Playwright API 完整参考手册

本手册详细列出 Phone-Playwright 提供的 Python 原生 API（异步与同步）、选择器规范与 MCP 协议工具接口。

---

## 1. 顶层入口类

### `AsyncPhonePlaywright` (异步环境)
```python
from phone_playwright.api.async_api import AsyncPhonePlaywright

async with AsyncPhonePlaywright() as pw:
    page = await pw.connect(device_id="192.168.1.3:43037")
    ...
```

### `SyncPhonePlaywright` (同步环境)
```python
from phone_playwright.api.sync_api import SyncPhonePlaywright

with SyncPhonePlaywright() as pw:
    page = pw.connect(device_id="192.168.1.3:43037")
    ...
```

---

## 2. Page API (`PhonePage` / `SyncPhonePage`)

| 方法 | 参数 | 返回值 | 说明 |
|---|---|---|---|
| `snapshot(include_screenshot=False)` | `include_screenshot: bool` | `PageSnapshot` | 获取当前屏幕紧凑语义快照，自动温热 1.0s 执行缓存。若参数为 True，回填 Base64 截图 |
| `locator(selector)` | `selector: str` | `PhoneLocator` | 构造惰性定位器对象 |
| `get_by_text(text, exact=False)` | `text: str, exact: bool` | `PhoneLocator` | 按显示文本或内容描述定位 |
| `get_by_role(role, name=None)` | `role: str, name: str \| None` | `PhoneLocator` | 按语义角色（Button, Input, CheckBox 等）定位 |
| `get_by_test_id(test_id)` | `test_id: str` | `PhoneLocator` | 按 Android resource-id 定位 |
| `swipe(direction, distance_ratio=0.5)` | `direction: Literal["up","down","left","right"], distance_ratio: float` | `None` | 执行全屏相对距离滑动手势，立即清空温热缓存 |
| `press_back()` | 无 | `None` | 触发系统返回键 (KEYCODE_BACK) |
| `press_home()` | 无 | `None` | 触发系统 Home 键 (KEYCODE_HOME) |
| `press_key(key_code)` | `key_code: int` | `None` | 触发指定 Android 键码 |
| `close()` | 无 | `None` | 断开连接并释放底层驱动资源 |

---

## 3. Locator API (`PhoneLocator` / `SyncPhoneLocator`)

| 方法 | 参数 | 返回值 | 说明 |
|---|---|---|---|
| `click(timeout_s=5.0)` | `timeout_s: float` | `ActionResult` | 自动等待元素 Attached -> Visible -> Stable -> Enabled 并执行中心点点击 |
| `fill(text, timeout_s=5.0)` | `text: str, timeout_s: float` | `ActionResult` | 自动定位输入框，通过广播剪贴板或 IME 输入文本（对中文字符与特殊字符天然安全） |
| `hover(timeout_s=5.0)` | `timeout_s: float` | `ActionResult` | 等待并悬停于元素上方（主要用于 iOS 或支持指针的平板） |
| `wait_for(state="visible", timeout_s=5.0)` | `state: Literal["visible", "hidden"], timeout_s: float` | `ActionResult` | 断言并等待元素变为可见或隐藏状态 |
| `scroll_into_view(max_swipes=5, direction="up", distance_ratio=0.5)` | `max_swipes: int, direction: str, distance_ratio: float` | `PhoneLocator` | 启动滑动搜寻循环，直到元素进入有效物理视口内 |
| `is_visible()` | 无 | `bool` | 瞬时检查元素在当前视口内是否可见（非阻塞） |
| `count()` | 无 | `int` | 统计当前视口内匹配该选择器的元素总数 |
| `text_content()` | 无 | `str \| None` | 获取首个匹配元素的文本内容或内容描述 |

---

## 4. 选择器语法规范

Phone-Playwright 支持多种灵活且具备容错能力的选择器策略：

1. **紧凑数字索引引用 (`@index`)**：
   - 语法：`@1`, `@2`, `@15`
   - 映射：直接对应最新一次 `snapshot()` 返回列表中标记的元素索引。
2. **文本匹配 (`text=...`)**：
   - 语法：`text=设置`, `text=无线局域网`
   - 规则：模糊包含匹配；大小写敏感度低；同时匹配 `text` 与 `content-desc`。
3. **精准资源标识符 (`resource-id=...`)**：
   - 语法：`resource-id=com.android.settings:id/search_action_bar` 或简写 `id=...`。
4. **语义角色匹配 (`role=...`)**：
   - 语法：`role=Button`, `role=Input`, `role=CheckBox`。
5. **复合属性过滤**：
   - 语法：`role=Button[name='确定']`。

---

## 5. 异常体系与诊断分类

所有异常均继承自 `PhonePlaywrightError`：

```text
PhonePlaywrightError
├── DeviceConnectionError        # 设备未找到、ADB 离线或授权拒绝
├── ActionabilityTimeoutError    # 可用性状态机超时 (通用基类)
│   ├── SelectorNotFoundError   # 元素不仅在视口中缺失，在整个屏幕 DOM 树中均不存在
│   └── OffscreenElementError   # 元素存在于 DOM 树中，但因长列表滚动处于当前视口之外
└── DriverError                 # 底层 ADB 命令或 WDA 请求返回严重硬件异常
```

---

## 6. MCP Server STDIO 协议工具接口

运行 `python scripts/cli.py --device <id> mcp` 时，提供如下符合 MCP 规范的标准 Tools：

- `phone_snapshot(device_id, include_screenshot=False)`: 输出当前界面的 Markdown 表格与当前 Activity。
- `phone_click(device_id, selector, timeout_s=5.0)`: 带自动等待的元素点击。
- `phone_fill(device_id, selector, text, timeout_s=5.0)`: 文本输入。
- `phone_swipe(device_id, direction, distance_ratio=0.5)`: 滑动手势。
- `phone_scroll_into_view(device_id, selector, max_swipes=5)`: 滚动元素进视口。
- `phone_press_key(device_id, key)`: 支持 "back", "home", "enter" 或数字键码。
