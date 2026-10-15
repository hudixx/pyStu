"""第 56 课示例：async def 里的 time.sleep 会把事件循环堵住。

对照 Netty 的事件循环线程里不能做阻塞调用。
两个各睡 0.2 秒的任务，一起等待应该接近 0.2 秒，而不是 0.4 秒。
本文件没有 FastAPI。先把「堵住」和「让出」的秒数差看清楚。
"""

from __future__ import annotations

import asyncio  # 事件循环、gather、会让出的 sleep。对照 Netty 的 EventLoop，不是 new Thread。
import time  # time.sleep 会占住当前线程。perf_counter 用来量墙上时间。对照 nanoTime。


async def block() -> None:
    """错误示范。time.sleep 不把控制权交回去，另一个任务只能干等。

    函数虽然写成了 async def，里面却没有 await。调用它得到协程，但一跑起来就占住线程 0.2 秒。
    对照在 Netty 的 IO 线程里 Thread.sleep。事件循环上只有这一条线程在干活。
    """
    time.sleep(0.2)


async def wait() -> None:
    """正确示范。asyncio.sleep 会让出事件循环，另一个任务可以同时睡。

    await 到点之前，循环可以去跑别的协程。两个 wait() 的 0.2 秒是重叠的，不是首尾相接。
    """
    await asyncio.sleep(0.2)


async def elapsed(job) -> float:
    """两个同样的任务一起跑，返回墙上的秒数。

    job 是函数本身，不是已经在跑的协程。对照传入 Runnable，由这里负责调用两次。
    传 block 或 wait 都行，因为两者都是「调用后得到协程」的 async def。
    """
    started = time.perf_counter()  # 秒，float。只和自己相减，不要拿去对日历时间。
    # job() 得到一个协程对象。调用两次，得到两个互相独立的任务。
    # gather 等两个都结束。它们是否重叠，取决于里面有没有把控制权交回去。
    # 对照把两个任务交给同一个事件循环，而不是 new 两个线程。
    await asyncio.gather(job(), job())
    return time.perf_counter() - started


def health() -> dict:
    """健康检查只回答进程还在。不查模型，不查库。对照 k8s 的 liveness。

    普通 def，不是 async def。里面没有网络、没有 sleep，调用它会立刻返回。
    这种函数放在 async 路由里直接调用是可以的。一旦里面加上 time.sleep 或同步的数据库调用，就会堵住循环。
    """
    return {"status": "ok"}


async def main_async() -> None:
    # 传入函数，不要写成 elapsed(block())。加了括号就是已经创建一个协程，elapsed 还会再调用它，类型对不上。
    blocked = await elapsed(block)  # 两个 time.sleep 串成一队。预期接近 0.40 秒。
    waited = await elapsed(wait)  # 两个 asyncio.sleep 重叠。预期接近 0.20 秒。
    # :.2f 是格式：保留两位小数。这是打印形式，不是把 float 修成两位再拿去比较。
    print(f"堵住 {blocked:.2f} 秒")
    print(f"让出 {waited:.2f} 秒")
    # health 是普通函数，没有 await。它立刻返回，不把循环交出去，但也不占时间。
    print("健康", health())


def main() -> None:
    # 同步入口。asyncio.run 创建循环、跑完 main_async、再关掉循环。不要在另一个 async def 里套它。
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
