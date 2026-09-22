# 第 16 课：从 HttpClient 看 httpx

Java 用 `HttpClient` / OkHttp / RestTemplate。
Python 标准库有 `urllib.request`，能用但啰嗦。日常用 **httpx**（同步 + 异步同一套 API），老项目常见 `requests`。

本课示例 **不访问公网**：在本机起一个最小 HTTP 服务，再用 httpx 去调。

先激活 venv 并装过 `.[web]`（见第 15 课）。然后：

```bash
PYTHONUTF8=1 python 16-HTTP客户端/16_httpx.py
```

---

## 1. 对照

| Java | Python |
|---|---|
| `HttpClient.newHttpClient()` | `httpx.Client()` 或直接 `httpx.get` |
| `HttpRequest.newBuilder().uri(...).GET()` | `client.get(url)` |
| `BodyHandlers.ofString()` | `response.text` / `response.json()` |
| 状态码 `statusCode()` | `response.status_code` |
| 超时 `Duration.ofSeconds(3)` | `timeout=3.0` |
| try-with-resources 关连接 | `with httpx.Client() as client:` |

```python
import httpx

with httpx.Client(timeout=3.0) as client:
    r = client.get("http://127.0.0.1:8000/ping")
    r.raise_for_status()          # 4xx/5xx 抛异常，类似非 2xx 自己判断
    data = r.json()               # 解析 JSON → dict/list
```

一次性脚本可以用 `httpx.get(url)`；多次请求请复用 `Client`（连接池），不要每次 new 一个。

POST JSON：

```python
r = client.post(url, json={"name": "hudi"})  # 自动 Content-Type: application/json
```

查询参数：`client.get(url, params={"q": "python"})` → `?q=python`。

---

## 2. 失败怎么处理

```python
try:
    r = client.get(url, timeout=2.0)
    r.raise_for_status()
except httpx.HTTPStatusError as e:
    # 有响应，但是 4xx/5xx
    print("状态码", e.response.status_code)
except httpx.RequestError as e:
    # 连不上、超时、DNS
    print("请求失败", e)
```

这比 `urllib` 的异常树好懂，接近你在 Java 里抓 `IOException` / 自己判断 status。

---

## 3. 和 `requests` 的关系

`requests` 只有同步。`httpx` 的 `Client` 对标 requests，`AsyncClient` 以后写 FastAPI 后台任务时还能用。
新代码优先 httpx。看到老教程用 requests，API 几乎能一对一翻译。

---

## 本课肌肉记忆

1. 多次请求用 `with httpx.Client() as client`
2. JSON 用 `.json()`；发送 JSON 用 `json={...}`
3. `raise_for_status()` 处理非 2xx
4. 超时一定要设，默认可能挂很久
5. 本课示例的服务端只为了练习，下一课开始用 FastAPI 当正经服务端

下一课 pydantic：对标 Bean Validation / DTO。
