# 第 23 课：从 Future.cancel 看超时与 TaskGroup

调模型、打检索，慢是常态。必须能 **超时取消**，并且一个检索失败时不要让其它任务继续空烧。

运行示例：

```bash
PYTHONUTF8=1 python 23-超时取消与TaskGroup/23_任务.py
```

---

## 1. 超时：`asyncio.timeout`（3.11+）

```python
async def slow() -> str:
    await asyncio.sleep(1.0)
    return "命中"

async def search() -> None:
    try:
        async with asyncio.timeout(0.2):
            await slow()
    except TimeoutError:
        print("0.2 秒还没回来")
```

超时后，里面的任务会被 **取消**。老写法 `await asyncio.wait_for(slow(), timeout=0.2)` 效果类似，博客里常见，能看懂即可。

| Java | Python |
|---|---|
| `future.get(200, MILLISECONDS)` | `async with asyncio.timeout(0.2)` |
| `TimeoutException` | `TimeoutError`（内置，不是 asyncio 专属名） |
| `future.cancel(true)` 发中断 | 抛 `CancelledError` 进被等的协程 |

---

## 2. 取消是协作的，不是 `Thread.stop`

Java 的 `cancel(true)` 是发 interrupt，对方要检查 `interrupted` 或在可中断的阻塞上醒来。
asyncio 更硬：取消时往协程里丢 `CancelledError`。它继承 **`BaseException`**，不是 `except Exception` 能吞掉的（这是好事）。

如果你写了：

```python
async def bad() -> None:
    try:
        await asyncio.sleep(10)
    except BaseException:
        pass    # 连取消都吞掉 → 超时失效
```

超时就废了。需要清理资源时：

```python
async def good() -> None:
    try:
        await asyncio.sleep(10)
    finally:
        ...     # 关连接；不要吞掉 CancelledError
```

对照：`catch (InterruptedException)` 之后要保留中断状态。这里是：别把 `CancelledError` 当普通业务异常吃掉。

---

## 3. TaskGroup：一个失败，取消兄弟

```python
async def boom() -> None:
    await asyncio.sleep(0.05)
    raise RuntimeError("检索失败")

async def other() -> None:
    try:
        await asyncio.sleep(2)
        print("other 跑完")      # 正常情况下看不到
    except asyncio.CancelledError:
        print("other 被取消")
        raise                   # 继续往上传，让 TaskGroup 知道

async def run() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(boom())
            tg.create_task(other())
    except ExceptionGroup as eg:
        print("组失败:", eg.exceptions)
```

`ExceptionGroup` 是 3.11 起的「一包异常」。TaskGroup 可能同时收到多个失败，所以不用普通的一个 `except RuntimeError`。

`asyncio.gather(boom(), other())` 默认：一个失败，**其它还在跑**，然后把第一个异常抛给你。这就是为什么新代码优先 TaskGroup——和 Java 21 `StructuredTaskScope` 同一个理由。

`gather(..., return_exceptions=True)` 会把异常当返回值，谁都不取消。适合「我就要全部跑完再汇总」。

---

## 4. 什么时候用哪一种

| 需求 | 写法 |
|---|---|
| 一组任务，失败就停 | `TaskGroup` |
| 只要其中一个结果 | 先 TaskGroup / gather，再自己挑；或 `asyncio.wait(..., FIRST_COMPLETED)`（本课不强制） |
| 这个调用最多等 N 秒 | `async with asyncio.timeout(N)` |
| 全部跑完，失败也当数据 | `gather(..., return_exceptions=True)` |

---

## 本课肌肉记忆

1. 超时用 `asyncio.timeout`，到期是 `TimeoutError`
2. 取消靠 `CancelledError`，不要用 `except Exception` 之外的大网去吞 `BaseException`
3. `TaskGroup` 一个失败会取消同组任务
4. `gather` 老代码能看懂；默认不取消兄弟
5. `finally` 里做清理，不要 `pass` 掉取消

下一课：把协程接到真 HTTP 上（`httpx.AsyncClient`），并讲清 **什么时候不要 async**。
