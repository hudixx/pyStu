"""第 28 课示例：stream=True，边收边打。

对照 Java：SSE / BodyHandlers.ofLines，不是等完整 body。
delta.content 可能是 None，必须判断。
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
            messages=[{"role": "user", "content": "你好, hudi"}],
            stream=True,
        )
        parts: list[str] = []
        async for chunk in stream:
            # 有的块 choices 为空；有的 delta.content 是 None。
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if not delta:
                continue
            print(delta, end="", flush=True)  # flush：否则一行结束才显示
            parts.append(delta)
        print()
        print("拼接 =", "".join(parts))
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
