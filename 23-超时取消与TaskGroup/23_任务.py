"""第 23 课示例：超时、协作式取消、TaskGroup 失败取消兄弟。

对照 Java：
- asyncio.timeout ≈ future.get(timeout)
- TimeoutError ≈ TimeoutException
- CancelledError ≈ 中断；它是 BaseException，不是普通 Exception
- TaskGroup + ExceptionGroup ≈ StructuredTaskScope 一个失败取消兄弟
"""

from __future__ import annotations

import asyncio


async def slow_search() -> str:
    """假装一次很慢的检索。"""
    await asyncio.sleep(1.0)
    return "命中"


async def demo_timeout() -> None:
    """0.2 秒等不到就放弃。slow_search 会被取消，不会在后台偷偷跑完。"""
    try:
        async with asyncio.timeout(0.2):
            result = await slow_search()
            print("不该看到成功:", result)
    except TimeoutError:
        print("超时：0.2s 内检索没有回来")


async def boom() -> None:
    """很快失败。用来示范 TaskGroup 取消兄弟。"""
    await asyncio.sleep(0.05)
    raise RuntimeError("检索失败")


async def other() -> None:
    """本该睡 2 秒。兄弟 boom 失败后，这里应收到 CancelledError。"""
    try:
        await asyncio.sleep(2)
        print("other 跑完了")  # 正常路径不应打印
    except asyncio.CancelledError:
        print("other 被取消（兄弟失败了）")
        raise  # 必须再抛出，不能吞掉，否则取消协议被破坏


async def demo_group() -> None:
    """一个失败 → 取消同组其它任务 → 把错误打成 ExceptionGroup 抛出。"""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(boom())
            tg.create_task(other())
    except ExceptionGroup as eg:
        # ExceptionGroup.exceptions 是一组子异常。这里应能看到 RuntimeError。
        print("TaskGroup 失败，子异常类型 =", [type(e).__name__ for e in eg.exceptions])


async def demo_wait_for() -> None:
    """老写法 wait_for，博客常见。效果和 timeout 上下文类似。"""
    try:
        await asyncio.wait_for(slow_search(), timeout=0.2)
    except TimeoutError:
        print("wait_for 同样超时")


async def main() -> None:
    print("=== 超时 ===")
    await demo_timeout()
    await demo_wait_for()
    print("=== TaskGroup 一个失败取消兄弟 ===")
    await demo_group()


if __name__ == "__main__":
    asyncio.run(main())
