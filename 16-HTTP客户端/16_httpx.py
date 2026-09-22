"""第 16 课示例：本机起服务，再用 httpx 去调。不访问公网。"""

from __future__ import annotations

import sys
from pathlib import Path

# 目录名带连字符，不能当包 import。把本目录塞进 sys.path 后即可 import demo_server。
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx

from demo_server import start_server


def main() -> None:
    server, base = start_server()
    try:
        with httpx.Client(timeout=3.0) as client:
            ping = client.get(f"{base}/ping")
            ping.raise_for_status()
            print("GET /ping =", ping.json())

            echoed = client.post(f"{base}/echo", json={"name": "hudi"})
            echoed.raise_for_status()
            print("POST /echo =", echoed.json())

            missing = client.get(f"{base}/nope")
            print("GET /nope 状态码 =", missing.status_code)
            try:
                missing.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("raise_for_status 抓住了", e.response.status_code)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
