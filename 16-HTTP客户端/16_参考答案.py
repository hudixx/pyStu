"""第 16 课参考答案。

题 1 / 2 你已经做对：GET 打出 pong，POST 打出 {'echo': {'lang': 'python'}}，
finally 里 shutdown 了。下面是一份更贴题目的精简版（不必抄 404 演示）。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 直接 python 本文件时，脚本目录已经在 sys.path[0]，所以你这次没写也能 import。
# 从别的目录 import 本模块时没有这一步会 ModuleNotFoundError，养成习惯写上。
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx

from demo_server import start_server


def main() -> None:
    server, base = start_server()
    try:
        with httpx.Client(timeout=3.0) as client:
            ping = client.get(f"{base}/ping")
            ping.raise_for_status()
            print(ping.json()["msg"])  # pong

            echo = client.post(f"{base}/echo", json={"lang": "python"})
            echo.raise_for_status()
            print(echo.json())  # {'echo': {'lang': 'python'}}
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
