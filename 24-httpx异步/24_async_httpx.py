"""第 24 课示例：AsyncClient 并发打两个本机 HTTP。不访问公网。

对照 Java：
- httpx.AsyncClient ≈ WebClient（异步 HTTP）
- await client.get ≈ 一次订阅 / await 响应
- async with Client ≈ try-with-resources 关连接池
- TaskGroup 两个请求 ≈ 两个 WebClient 调用并行等

靶子复用第 16 课 demo_server：本课只换客户端。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# 目录名带连字符，不能当包 import。把 16 课目录插到搜索路径最前。
_SIXTEEN = Path(__file__).resolve().parent.parent / "16-HTTP客户端"
sys.path.insert(0, str(_SIXTEEN))

import httpx

from demo_server import start_server


async def hit(base: str) -> None:
    """复用一个 AsyncClient，并发 GET /ping 和 POST /echo。"""
    # timeout=3.0：连接+读的上限。模型 API 以后会设得更大，但必须有超时。
    async with httpx.AsyncClient(timeout=3.0) as client:
        async with asyncio.TaskGroup() as tg:
            # create_task 立刻返回；两个请求同时在飞。
            t_ping = tg.create_task(client.get(f"{base}/ping"))
            t_echo = tg.create_task(
                client.post(f"{base}/echo", json={"name": "hudi"})
            )
        # with 结束：两个都有结果（或抛了异常）。
        ping = t_ping.result()
        echo = t_echo.result()
        ping.raise_for_status()
        echo.raise_for_status()
        print("GET /ping =", ping.json())
        print("POST /echo =", echo.json())


def main() -> None:
    # 服务端仍是同步的 ThreadingHTTPServer，没问题：它在自己的线程里听端口。
    server, base = start_server()
    try:
        # 客户端这边才是事件循环。不要在已经 async 的函数里再 asyncio.run。
        asyncio.run(hit(base))
    finally:
        # 无论成功失败都关服务，否则进程可能挂着。
        server.shutdown()


if __name__ == "__main__":
    main()
