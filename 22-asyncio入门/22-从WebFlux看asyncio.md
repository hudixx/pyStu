# 第 22 课：从 WebFlux 看 asyncio

第 12 课：IO 用线程池，CPU 用进程池，asyncio 只提了一句。
现在要会写，因为模型 API、流式输出、并发检索全是「等网络」。

对照：Java 的 NIO / Netty 事件循环 / WebFlux。**不是**再开一套线程。

运行示例（大约 1 秒多）：

```bash
PYTHONUTF8=1 python 22-asyncio入门/22_asyncio.py
```

---

## 1. 三种并发，现在用第三种

| 方式 | 几条线程 | 适合 | 第几课 |
|---|---|---|---|
| `ThreadPoolExecutor` | N | IO，写法简单 | 12 |
| `ProcessPoolExecutor` | N 个进程 | CPU | 12 |
| `asyncio` 事件循环 | **1**（默认） | 大量等待 IO | 本课 |

四个 `sleep(0.2)`：

- 串行 ≈ 0.8s
- 线程池 ≈ 0.2s（四条线程各自阻塞）
- asyncio ≈ 0.2s（**一条线程**，谁该等就把控制权交回去）

数字看起来和线程池一样，机制不同。线程是操作系统帮你切换；asyncio 是函数写了 `await` 才切换。忘了 `await`，事件循环就被堵住——和在 Netty 的 event loop 里调用 `Thread.sleep` 是同一类事故。

---

## 2. `async def` 返回的不是结果

```python
async def wait_one(name: str) -> str:
    await asyncio.sleep(0.2)   # 把这 0.2 秒的等待让出去
    return name
```

`wait_one("a")` **不会**等 0.2 秒。它只造出一个协程对象，像你 `new CompletableFuture()` 但还没开始跑。

真正跑：

```python
import asyncio

asyncio.run(wait_one("a"))     # 脚本入口：起事件循环，跑完再关
```

已经在异步函数里时，用 `await wait_one("a")`。

| Java | Python |
|---|---|
| `Mono<String> m = waitOne("a")` | `wait_one("a")` 得到 coroutine |
| `m.block()` / `subscribe` | `asyncio.run(...)` 或 `await` |
| 事件循环线程 | `asyncio.run` 起的那条线程 |
| 在 event loop 里 `Thread.sleep` | 在 `async def` 里 `time.sleep` |

不能在普通 `def` 里写 `await`，语法就报错。也不能在已经运行的循环里再 `asyncio.run`（FastAPI 自己有循环，接口里用 `await`，不要再 `run`）。

---

## 3. 并发：`TaskGroup`（3.11+，你是 3.13）

```python
async def together() -> list[str]:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(wait_one("a"))
        t2 = tg.create_task(wait_one("b"))
    # 离开 with 时两个都结束了（成功或失败）
    return [t1.result(), t2.result()]
```

老代码常见 `asyncio.gather(wait_one("a"), wait_one("b"))`。能看懂即可。新代码优先 TaskGroup：一个失败会取消同组其它任务（下一课细讲）。

对照 Java 21 的 `StructuredTaskScope`。没碰过 Loom 就记：一组任务，一起开始，一起收。

---

## 4. 必须用 `asyncio.sleep`，不要 `time.sleep`

`time.sleep` 卡住 **整条** 事件循环线程，同循环里其它协程全部饿死。
`await asyncio.sleep(...)` 才是「我去等，你可以跑别人」。

示例文件后半段会打印两种写法的耗时：错误写法接近相加，正确写法接近取 max。

---

## 5. 和 FastAPI 的关系（先知道，别改第 19 课）

FastAPI 允许 `async def` 当接口。阶段四用普通 `def` 是对的：当时没有慢 IO。
等你真的 `await` 模型 SDK 时再改。没有 `await` 的 `async def` 是伪装，还可能让人误以为它不阻塞。

---

## 本课肌肉记忆

1. `async def` 调用得到协程，必须 `await` 或交给 `asyncio.run` / `TaskGroup`
2. 默认一条线程；切换发生在 `await`
3. 等时间用 `asyncio.sleep`，禁止在协程里 `time.sleep`
4. 并发用 `TaskGroup`，不必先开线程
5. 普通 `def` 里不能 `await`

下一课：超时、取消、一个失败如何带倒一组任务。
