"""第 22 课示例：async def / await / TaskGroup / 堵住事件循环。

对照 Java：
- asyncio.run ≈ 启动 Netty 事件循环，跑完一个入口任务再退出
- async def 返回 coroutine ≈ 得到 Mono / CompletableFuture，还没执行
- await ≈ 把等待让出去，不是再开一条线程
- TaskGroup ≈ Java 21 StructuredTaskScope
- time.sleep 在协程里 ≈ 在 event loop 线程里 Thread.sleep
"""

from __future__ import annotations

import asyncio
import time


async def wait_one(name: str, seconds: float) -> str:
    """异步等待。await sleep 会把这几秒让给事件循环上的其它任务。"""
    # asyncio.sleep 不是 time.sleep：它登记「N 秒后再叫醒我」，然后交出控制权。
    await asyncio.sleep(seconds)
    return name


async def serial() -> list[str]:
    """一个等完再等下一个。四个 0.2s 大约 0.8s。"""
    out: list[str] = []
    for name in ("a", "b", "c", "d"):
        # 这里有 await，所以是真的串行等待。
        out.append(await wait_one(name, 0.2))
    return out


async def concurrent() -> list[str]:
    """四个一起等。总时间大约 0.2s，仍然只有一条线程。"""
    async with asyncio.TaskGroup() as tg:
        # create_task：把协程交给事件循环调度，马上返回 Task，并不等它结束。
        tasks = [tg.create_task(wait_one(name, 0.2)) for name in ("a", "b", "c", "d")]
    # 离开 with 时全部结束。result() 取返回值；若任务里抛过异常，这里会再抛。
    return [t.result() for t in tasks]


async def blocked_pair() -> None:
    """错误示范：协程里 time.sleep，两个 0.3s 会变成约 0.6s。"""
    async def stuck() -> None:
        # 堵住整条事件循环线程。另一个 stuck 根本跑不起来，只能排队。
        time.sleep(0.3)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(stuck())
        tg.create_task(stuck())


async def yielded_pair() -> None:
    """正确：两个 0.3s 重叠，大约 0.3s。"""
    async def loose() -> None:
        await asyncio.sleep(0.3)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(loose())
        tg.create_task(loose())


def timed(label: str, seconds: float) -> None:
    """统一打印秒数，方便对数量级。"""
    print(f"{label}: {seconds:.2f}s")


def main() -> None:
    # 只调用、不 await：得到 coroutine 对象。对照 new 了一个没订阅的 Mono。
    leftover = wait_one("漏掉 await", 0.1)
    print("没 await 时拿到的是", type(leftover).__name__)
    # 不 close 的话，解释器退出时会 RuntimeWarning: coroutine was never awaited。
    leftover.close()

    t0 = time.perf_counter()
    print("串行结果 =", asyncio.run(serial()))
    timed("串行 4×0.2s", time.perf_counter() - t0)

    t0 = time.perf_counter()
    print("并发结果 =", asyncio.run(concurrent()))
    timed("TaskGroup 4×0.2s", time.perf_counter() - t0)

    t0 = time.perf_counter()
    asyncio.run(blocked_pair())
    timed("错误：两个 time.sleep(0.3) 放进 TaskGroup", time.perf_counter() - t0)

    t0 = time.perf_counter()
    asyncio.run(yielded_pair())
    timed("正确：两个 asyncio.sleep(0.3)", time.perf_counter() - t0)


if __name__ == "__main__":
    main()
