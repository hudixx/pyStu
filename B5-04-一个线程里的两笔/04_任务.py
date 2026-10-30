"""选修 B5 第 4 课：一条线程上有两笔任务时，threading.local 只有一份。

对照 ThreadLocal。Java 里常常一笔请求占住一条线程，所以能隔开。
asyncio 是很多笔请求轮流用同一条线程。local 跟着线程走，两笔改的是同一格。
contextvars 在创建任务时复制一份，await 回来还是自己的号。

await 本身不换线程。只有一笔任务时，await 之后 local 还是它的。
串号是因为中间另一笔改了同一份。本课用 sleep(0) 把这个空档露出来。不装 OpenTelemetry。
"""

from __future__ import annotations

import asyncio  # gather、sleep、run。事件循环在一条线程上轮流跑这些协程。对照 Netty 的 EventLoop，不是 new Thread。
import contextvars  # 每个任务一份上下文。创建任务时复制，不跟线程走。
import threading  # local 跟线程走。这条线程上只有一格。对照 ThreadLocal。


# 跟着线程走。这条线程上的所有任务看见的是同一格。
# local() 造出一个空的线程局部对象。这时还没有 value 这个属性。对照 new ThreadLocal<>()。
local = threading.local()
# 跟着上下文走。每个任务创建时复制一份。
# default="-" 是还没 set 时 get 到的值。和上一课一样，槽在模块里只有一个对象，值可以各任务不同。
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


async def worker(name: str) -> None:
    """先写下自己的号，让出一次，再读。中间另一笔会改掉 local。

    逻辑：
    1. 把 name 写进 local.value，再 set 到 trace_id。
    2. await sleep(0)，立刻把这条线程让给另一笔任务。
    3. 再读。local 是线程上的同一格，会被后写的那笔盖掉。context 是本任务自己的副本，仍是自己的 name。
    async def 才能写 await。调用 worker("A") 不会马上跑完，只得到一个协程，要交给事件循环。
    """

    local.value = name  # 没有 value 这个属性时，第一次赋值会建出来。
    # threading.local 上的属性是临时长出来的。对照 ThreadLocal.set。这条线程上后写的会盖住先写的。
    trace_id.set(name)  # 写进当前任务的上下文。这里不用留 token，因为任务结束就丢掉这份上下文。
    await asyncio.sleep(0)  # 马上让出。不等待。另一笔任务会在这一空档里运行。
    # sleep(0) 不是 time.sleep。它会把控制权交回事件循环。time.sleep 会把这条线程堵住，另一笔插不进来，串号就看不见了。
    # await 才真正等待。不写 await，sleep(0) 只是一个没人跑的协程，让出不会发生。
    # getattr 的第三个值是还没有 value 时用的。这里让出之后，value 已经被后写的那笔盖过。
    # getattr(local, "value", "-") 对照：属性还没有就用 "-"，不要抛 AttributeError。本课让出之后属性一定在，只是值可能变成对方的。
    print(name, "local", getattr(local, "value", "-"), "context", trace_id.get())


async def run() -> None:
    """把 A、B 两笔排进同一个事件循环，一起等到它们都结束。

    gather 收到两个协程。先开始的那笔跑到 await 就让出，另一笔才能插进来改 local。
    不加 gather、只 await worker("A") 再 await worker("B")，两笔是前后做完，中间没有「对方在我让出时改同一格」。
    """

    # gather 两笔一起排上。先排到的先跑到第一个 await。
    # worker("A") 加了括号：先得到协程对象。gather 负责把它们跑起来。对照提交两个任务给同一个事件循环。
    await asyncio.gather(worker("A"), worker("B"))


def main() -> None:
    """同步入口。asyncio.run 新建事件循环，把 run 跑完，再关掉循环。

    不要在另一个 async def 里再套 asyncio.run。这里是普通函数，所以可以。
    """

    asyncio.run(run())


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# asyncio 的两笔任务轮流用同一条线程。threading.local 跟着线程，所以 A 让出之后，B 写的 value 会盖住 A 的。
# contextvars 在每个任务创建时复制一份。await 回来，A 读到的仍是 A，B 读到的仍是 B。
# await 本身不换线程。串号是因为让出的空档里，另一笔改了同一格。sleep(0) 就是故意把这个空档露出来。
