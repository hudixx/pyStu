"""选修 B5 第 4 课：一条线程上有两笔任务时，threading.local 只有一份。

对照 ThreadLocal。Java 里常常一笔请求占住一条线程，所以能隔开。
asyncio 是很多笔请求轮流用同一条线程。local 跟着线程走，两笔改的是同一格。
contextvars 在创建任务时复制一份，await 回来还是自己的号。

await 本身不换线程。只有一笔任务时，await 之后 local 还是它的。
串号是因为中间另一笔改了同一份。本课用 sleep(0) 把这个空档露出来。不装 OpenTelemetry。
"""

from __future__ import annotations

import asyncio
import contextvars
import threading

# 跟着线程走。这条线程上的所有任务看见的是同一格。
local = threading.local()
# 跟着上下文走。每个任务创建时复制一份。
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


async def worker(name: str) -> None:
    """先写下自己的号，让出一次，再读。中间另一笔会改掉 local。"""

    local.value = name  # 没有 value 这个属性时，第一次赋值会建出来。
    trace_id.set(name)
    await asyncio.sleep(0)  # 马上让出。不等待。另一笔任务会在这一空档里运行。
    # getattr 的第三个值是还没有 value 时用的。这里让出之后，value 已经被后写的那笔盖过。
    print(name, "local", getattr(local, "value", "-"), "context", trace_id.get())


async def run() -> None:
    # gather 两笔一起排上。先排到的先跑到第一个 await。
    await asyncio.gather(worker("A"), worker("B"))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
