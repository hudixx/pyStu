"""第 24 课示例：AsyncClient 并发打两个本机 HTTP。不访问公网。

对照 Java：
- httpx.AsyncClient ≈ WebClient（异步 HTTP）
- await client.get ≈ 一次订阅 / await 响应
- async with Client ≈ try-with-resources 关连接池
- TaskGroup 两个请求 ≈ 两个 WebClient 调用并行等

靶子复用第 16 课 demo_server：本课只换客户端。
规则：函数体里真有 await，才写 async def。没有 await 却写成 async 是伪装。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# 目录名「16-HTTP客户端」带连字符，不能写成 import 16-HTTP客户端.demo_server。
# parent.parent：从 24-httpx异步 回到项目根，再进 16 课目录。对照往 classpath 临时加一个文件夹。
_SIXTEEN = Path(__file__).resolve().parent.parent / "16-HTTP客户端"
sys.path.insert(0, str(_SIXTEEN))  # 插到最前，后面 from demo_server import 才能找到

import httpx  # 和第 16 课同一个库；本课用 AsyncClient，同步版是 httpx.Client

from demo_server import start_server  # 同步的 ThreadingHTTPServer，在它自己的线程里听端口


async def hit(base: str) -> None:
    """复用一个 AsyncClient，并发 GET /ping 和 POST /echo。

    两个请求重叠等待，总时间接近较慢的那一个，不是相加。
    若写成 ping = await get; echo = await post，那就是串行，白写了 async。
    """
    # timeout=3.0：连接+读的上限。模型 API 以后会设得更大，但必须有超时，默认可能挂很久。
    # async with：离开时关闭连接池。对照 try-with-resources 关 WebClient。
    async with httpx.AsyncClient(timeout=3.0) as client:
        async with asyncio.TaskGroup() as tg:
            # create_task 立刻返回 Task；两个请求同时在飞。
            # client.get 返回的是协程，必须挂到 Task 上或 await，不能当同步结果用。
            t_ping = tg.create_task(client.get(f"{base}/ping"))
            t_echo = tg.create_task(
                client.post(f"{base}/echo", json={"name": "hudi"})  # json= 自动 dumps + Content-Type
            )
        # with 结束：两个都有结果（或其中一个抛了，组失败）。result() 对照 Future.get()。
        ping = t_ping.result()
        echo = t_echo.result()
        # 和第 16 课一样：4xx/5xx 默认不当异常，要自己 raise_for_status。
        ping.raise_for_status()
        echo.raise_for_status()
        print("GET /ping =", ping.json())   # 应看到 {"ok": true, "msg": "pong"}
        print("POST /echo =", echo.json())  # 应看到 {"echo": {"name": "hudi"}}


def main() -> None:
    """入口仍是普通 def：里面没有 await，阻塞在 asyncio.run 上是合理的。"""
    # 服务端仍是同步的 ThreadingHTTPServer，没问题：它在自己的线程里听端口，不占事件循环。
    server, base = start_server()
    try:
        # 客户端这边才是事件循环。不要在已经 async 的函数里再 asyncio.run（会 RuntimeError）。
        asyncio.run(hit(base))
    finally:
        # 无论成功失败都关服务，否则进程可能挂着。对照 server.stop()。
        server.shutdown()


if __name__ == "__main__":
    main()
