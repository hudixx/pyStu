"""第 23 课示例：超时、协作式取消、TaskGroup 失败取消兄弟。

对照 Java：
- asyncio.timeout ≈ future.get(timeout)
- TimeoutError ≈ TimeoutException
- CancelledError ≈ 中断；它是 BaseException，不是普通 Exception
- TaskGroup + ExceptionGroup ≈ StructuredTaskScope 一个失败取消兄弟

取消是协作的，不是 Thread.stop。超时后里面的 await 会收到 CancelledError，
任务不会在后台偷偷跑完。
"""

from __future__ import annotations

import asyncio


async def slow_search() -> str:
    """假装一次很慢的检索。模型 API / 向量库查询经常是这种「等 1 秒」的 IO。"""
    await asyncio.sleep(1.0)  # 把 1 秒让出去；若外层超时，这里会被取消，到不了 return
    return "命中"


async def demo_timeout() -> None:
    """0.2 秒等不到就放弃。slow_search 会被取消，不会在后台偷偷跑完。"""
    try:
        # asyncio.timeout(0.2)：进入 with 开始倒计时，超时则取消 with 块里正在 await 的东西。
        # 对照 future.get(200, MILLISECONDS)，到期抛 TimeoutException。
        async with asyncio.timeout(0.2):
            result = await slow_search()
            print("不该看到成功:", result)  # 1.0s > 0.2s，正常跑不到这里
    except TimeoutError:
        # TimeoutError 是内置异常，不是 asyncio.TimeoutError（3.11 起统一成内置名）。
        print("超时：0.2s 内检索没有回来")


async def boom() -> None:
    """很快失败。用来示范 TaskGroup 取消兄弟。"""
    await asyncio.sleep(0.05)  # 稍等一下，让 other 先挂上 sleep(2)
    raise RuntimeError("检索失败")  # 普通业务异常。TaskGroup 会抓住并取消同组其它 Task


async def other() -> None:
    """本该睡 2 秒。兄弟 boom 失败后，这里应收到 CancelledError。"""
    try:
        await asyncio.sleep(2)
        print("other 跑完了")  # 正常路径不应打印：还没到 2s 就被取消
    except asyncio.CancelledError:
        # CancelledError 继承 BaseException，except Exception 抓不住（这是好事，避免误吞取消）。
        # 对照 catch (InterruptedException) 之后要保留中断状态。
        print("other 被取消（兄弟失败了）")
        raise  # 必须再抛出，不能吞掉，否则取消协议被破坏，TaskGroup 会认为你还要跑


async def demo_group() -> None:
    """一个失败 → 取消同组其它任务 → 把错误打成 ExceptionGroup 抛出。"""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(boom())   # 约 0.05s 后炸
            tg.create_task(other())  # 会被取消，打印「other 被取消」
        # 组成功才会走到这里。本例 boom 失败，离开 with 时抛 ExceptionGroup。
    except ExceptionGroup as eg:
        # ExceptionGroup（3.11+）：一包异常。TaskGroup 可能同时收到多个失败，所以不是单个 RuntimeError。
        # eg.exceptions 是元组，里面才是真正的 RuntimeError。CancelledError 通常不会出现在这里。
        print("TaskGroup 失败，子异常类型 =", [type(e).__name__ for e in eg.exceptions])


async def demo_wait_for() -> None:
    """老写法 wait_for，博客常见。效果和 timeout 上下文类似。

    新代码优先 async with asyncio.timeout：可以包住多行 await，不必把一切塞进一个表达式。
    """
    try:
        # wait_for(协程, timeout=秒)：到期取消该协程，并抛 TimeoutError。
        await asyncio.wait_for(slow_search(), timeout=0.2)
    except TimeoutError:
        print("wait_for 同样超时")


async def main() -> None:
    """已经在协程里：用 await 调其它 async def，不要再 asyncio.run。"""
    print("=== 超时 ===")
    await demo_timeout()
    await demo_wait_for()
    print("=== TaskGroup 一个失败取消兄弟 ===")
    await demo_group()


if __name__ == "__main__":
    # 脚本入口：起事件循环、跑 main、退出。FastAPI 自己有循环，接口里只 await，不要再 run。
    asyncio.run(main())
