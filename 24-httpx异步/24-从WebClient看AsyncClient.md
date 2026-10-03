# 第 24 课：从 WebClient 看 AsyncClient

第 16 课的 `httpx.Client` 对标 `HttpClient` / OkHttp：同步，调用线程一直等到响应。
模型 API 一次要等几秒。写在 FastAPI 的 `async def` 里如果还用同步 Client，等于在 Netty 线程里同步调 HTTP——把整个 worker 堵住。

本课换 `AsyncClient`。靶子仍是第 16 课那个本机服务，不访问公网。

运行示例：

```bash
PYTHONUTF8=1 python 24-httpx异步/24_async_httpx.py
```

---

## 1. 对照

| Java | 同步 httpx（16 课） | 异步 httpx |
|---|---|---|
| `HttpClient.send` | `client.get(url)` | `await client.get(url)` |
| WebClient / reactor | — | `httpx.AsyncClient` |
| try-with-resources | `with httpx.Client()` | `async with httpx.AsyncClient()` |
| 连接池 | 复用 `Client` | 复用 `AsyncClient`，道理一样 |

```python
async with httpx.AsyncClient(timeout=3.0) as client:
    ping = await client.get(f"{base}/ping")
    ping.raise_for_status()
    echoed = await client.post(f"{base}/echo", json={"name": "hudi"})
```

`get` / `post` / `raise_for_status` / `.json()` 和同步版同一套，只是前面多 `await`，Client 换成 `AsyncClient`，`with` 换成 `async with`。

并发两个请求（阶段五结束标准的那句）：

```python
async with httpx.AsyncClient(timeout=3.0) as client:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(client.get(f"{base}/ping"))
        t2 = tg.create_task(client.post(f"{base}/echo", json={"n": 1}))
    t1.result().raise_for_status()
    t2.result().raise_for_status()
```

两个请求重叠等待，总时间接近较慢的那一个，不是相加。

---

## 2. 何时不要 async（和「别什么都上 WebFlux」同一句）

| 场景 | 做法 |
|---|---|
| 等 HTTP / 等数据库 IO | `async def` + 异步客户端 |
| CPU 密集 | 第 12 课进程池；别丢进事件循环 |
| SDK 只有同步阻塞 API | `await asyncio.to_thread(sync_fn, ...)`，或换官方异步 SDK |
| 接口里没有 `await` | 写成普通 `def`。第 18 / 19 课那样是对的 |
| `async def` 里 `time.sleep` / 同步 `httpx.get` / 大文件同步读 | **事故**：堵住整条事件循环 |

FastAPI 的细节，现在就要记住：

- 普通 `def`：框架把它丢到线程池，不会堵事件循环
- `async def`：跑在事件循环上。里面一旦出现阻塞调用，**这个 worker 上所有其它异步请求一起停**

所以规则很简单：**函数体里真有 `await`，才写 `async def`。** 没有 await 却写成 async，既没好处，还留下「看起来不阻塞、其实可能阻塞」的坑。

`asyncio.to_thread`：把同步函数丢到线程池，自己 `await` 那个等待。适合「暂时只有同步 SDK」：

```python
result = await asyncio.to_thread(blocking_sdk_call, prompt)
```

官方若提供 `AsyncOpenAI` 这类，优先用官方异步客户端，不要自己包一层同步再 to_thread。阶段六会碰到。

---

## 3. 和线程池怎么选

四个慢 HTTP：

- `ThreadPoolExecutor` + 同步 Client：能跑，线程数 = 并发数。几百个还能撑，几千个就贵
- `AsyncClient` + TaskGroup：一条线程撑大量等待中的连接

模型调用通常是「每请求几秒、并发几十」，两种都能用。选异步是因为后面流式（SSE）和 FastAPI 的 `async def` 是同一套事件循环，别混着堵。

小脚本、一次性同步工具，继续用第 16 课的 `Client` 完全没问题。

---

## 本课肌肉记忆

1. `async with httpx.AsyncClient() as client` + `await client.get`
2. 多次请求复用同一个 AsyncClient
3. 并发用 TaskGroup，不要串行两个 `await` 还以为自己并发了
4. 没有 `await` 就不要 `async def`
5. 阻塞 SDK 用官方异步版或 `asyncio.to_thread`，不要直接在协程里调用

下一课：ruff / mypy，让别人 clone 下来能检查，而不是只靠 IDE 红线。
