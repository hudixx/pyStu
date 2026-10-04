import sys
from pathlib import Path
import asyncio

import httpx

sys.path.insert(0,str(Path(__file__).resolve().parent.parent / "16-HTTP客户端"))

from demo_server import start_server

async def check(base_url: str) -> None:
    async with httpx.AsyncClient(timeout=3.0) as client:
        async with asyncio.TaskGroup() as tg:
            rs1 = tg.create_task(client.get(base_url+"/ping"))
            rs2 = tg.create_task(client.post(base_url+"/echo", json={"lang": "python"}))
        ping = rs1.result()
        post = rs2.result()
        ping.raise_for_status()
        post.raise_for_status()
        print(ping.json())
        print(post.json())
    with httpx.Client(timeout=3.0) as client:
        ping = client.get(base_url+"/ping")
        post = client.post(base_url+"/echo", json={"lang": "python"})
        ping.raise_for_status()
        post.raise_for_status()
        print(ping.json())
        print(post.json())

def main() -> None:
    server, base_url = start_server()
    try:
        asyncio.run(check(base_url))
    finally:
        server.shutdown()

if __name__ == '__main__':
   main()

"""
题2： 请帮忙在参考答案的注释中给出答案
"""

