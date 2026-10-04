"""第 24 课参考答案。题 1：AsyncClient + TaskGroup 并发 GET/POST 都对。

你多写的同步 Client 对比方向好，但不要放在 async def 里面。
那正是题 2 要拦的坑：事件循环线程上跑阻塞 HTTP。
对比请放到普通 def / main 里，asyncio.run 返回之后再跑。

题 2：
- 继续用 def + 同步 Client：小脚本、一次性工具、函数里没有 await、
  FastAPI 普通 def 接口（框架会丢线程池）。第 16 / 18 / 19 课那样是对的。
- FastAPI 的 async def 里调用同步 httpx.get：堵住整条事件循环，
  这个 worker 上其它异步请求一起停。对照在 Netty 线程里同步调 HTTP。
  要异步就用 AsyncClient；暂时只有同步 SDK 就 await asyncio.to_thread(...)。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "16-HTTP客户端"))

import httpx

from demo_server import start_server


async def check(base: str) -> None:
    """只做异步并发。没有 await 的同步对比不要写在这个函数里。"""
    async with httpx.AsyncClient(timeout=3.0) as client:
        async with asyncio.TaskGroup() as tg:
            t_ping = tg.create_task(client.get(f"{base}/ping"))
            t_echo = tg.create_task(
                client.post(f"{base}/echo", json={"lang": "python"})
            )
        ping = t_ping.result()
        echo = t_echo.result()
        ping.raise_for_status()
        echo.raise_for_status()
        print("async GET /ping =", ping.json())
        print("async POST /echo =", echo.json())


def check_sync(base: str) -> None:
    """同步版对比：普通 def，可以阻塞。放在 asyncio.run 之后调用。"""
    with httpx.Client(timeout=3.0) as client:
        ping = client.get(f"{base}/ping")
        echo = client.post(f"{base}/echo", json={"lang": "python"})
        ping.raise_for_status()
        echo.raise_for_status()
        print("sync GET /ping =", ping.json())
        print("sync POST /echo =", echo.json())


def main() -> None:
    server, base = start_server()
    try:
        asyncio.run(check(base))
        check_sync(base)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
