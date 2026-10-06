"""第 28 课参考答案。题 1 过：stream=True，逐块打印，拼接以「回声:」开头。

Path(__file__)、close、shutdown、空 choices / 空 delta 都跳过了，这些是对的。
model 写成 mock_model：假模型不看名字，真网关会 404。示例用 mock-chat。
环境变量名应是 OPENAI_API_KEY。Windows 不区分大小写，碰巧能读到；Linux 读不到。

题 2：
- 差在 HTTP 响应这一层。非流式等完整 body 再解析；流式是 text/event-stream，
  一块一块推（SSE）。对照 BodyHandlers.ofString() 和 ofLines()。
  不是必须上 WebSocket。
- delta.content 可能是 None：第一块常常只有 role，最后一块常常只有 finish_reason，
  中间才是字。空块要 continue，不要拿 None 去拼接。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def stream_once(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        stream = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "我是 hudi"}],
            stream=True,
        )
        parts: list[str] = []
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if not delta:
                continue
            print(delta, end="", flush=True)
            parts.append(delta)
        print()
        print("".join(parts))
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(stream_once(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
