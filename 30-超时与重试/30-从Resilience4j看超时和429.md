# 第 30 课：从 Resilience4j 看超时和 429

模型网关会慢、会限流、会断。你在 Java 里用 Resilience4j / 自己的重试器处理过支付渠道，这里换错误码，思路一样。

运行：

```bash
PYTHONUTF8=1 python 30-超时与重试/30_失败.py
```

应看到：慢请求超时、一直 429 最终失败、429-ONCE 靠 SDK 重试成功。

---

## 1. 超时

```python
client = AsyncOpenAI(..., timeout=0.3, max_retries=0)
```

假模型遇到 `TRIGGER:SLOW` 会先 `sleep(2)`。`timeout=0.3` 时 SDK 抛 `APITimeoutError`（或底层 `TimeoutError`）。

对照：`HttpClient` 的 `Duration.ofMillis(300)`。默认超时往往太长，模型调用 **必须显式写**。

---

## 2. 429 和 SDK 自带重试

HTTP 429 = 限流。官方 SDK 默认会重试 429 / 部分 5xx（指数退避）。

```python
client = AsyncOpenAI(..., timeout=10.0, max_retries=2)
```

| 假模型文案 | 行为 |
|---|---|
| `TRIGGER:429` | 每次都 429 → 重试耗尽 → `RateLimitError` |
| `TRIGGER:429-ONCE` | 第一次 429，第二次 200 → 开着重试时能成功 |

自己用 `while` 再套一层也可以，但先用 SDK 的 `max_retries`，别一上来上 tenacity。

**幂等：** `chat.completions` 默认不是业务幂等——重试可能真的再生成一次，多花一份钱。限流重试通常值得；对「创建订单式」副作用不要盲目重试。本课假模型没有副作用。

---

## 3. 常见异常

| 异常 | 何时 |
|---|---|
| `APITimeoutError` | 等太久 |
| `RateLimitError` | 429 |
| `APIStatusError` | 其它 4xx/5xx，里面有 `status_code` |
| `APIConnectionError` | 连不上 |

```python
from openai import APITimeoutError, RateLimitError

try:
    await client.chat.completions.create(...)
except APITimeoutError:
    print("超时")
except RateLimitError:
    print("限流")
```

不要裸 `except Exception` 把取消和编程错误一起吞掉（第 23 课）。

---

## 本课肌肉记忆

1. `timeout=` 必写
2. 429 先让 SDK `max_retries` 处理
3. 重试会花钱，知道即可
4. 捕获具体异常，对照你 catch `HttpTimeoutException` 而不是 `Exception`

下一课：把流式 + JSON 校验 + 超时，包成 FastAPI。阶段六收口。
