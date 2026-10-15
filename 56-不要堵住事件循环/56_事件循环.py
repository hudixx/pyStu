"""第 56 课示例：async def 里的 time.sleep 会把事件循环堵住。

对照 Netty 的事件循环线程里不能做阻塞调用。
两个各睡 0.2 秒的任务，一起等待应该接近 0.2 秒，而不是 0.4 秒。
"""

from __future__ import annotations

import asyncio
import time


async def block() -> None:
    """错误示范。time.sleep 不把控制权交回去，另一个任务只能干等。"""
    time.sleep(0.2)


async def wait() -> None:
    """正确示范。asyncio.sleep 会让出事件循环，另一个任务可以同时睡。"""
    await asyncio.sleep(0.2)


async def elapsed(job) -> float:
    """两个同样的任务一起跑，返回墙上的秒数。"""
    started = time.perf_counter()
    await asyncio.gather(job(), job())
    return time.perf_counter() - started


def health() -> dict:
    """健康检查只回答进程还在。不查模型，不查库。对照 k8s 的 liveness。"""
    return {"status": "ok"}


async def main_async() -> None:
    blocked = await elapsed(block)
    waited = await elapsed(wait)
    print(f"堵住 {blocked:.2f} 秒")
    print(f"让出 {waited:.2f} 秒")
    print("健康", health())


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
