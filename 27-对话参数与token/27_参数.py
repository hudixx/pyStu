"""第 27 课示例：temperature、max_tokens、usage。

对照：这些都是 JSON 请求字段，不是调参仪式。
usage 三个数字对标账单，不是调试装饰。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def show(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        full = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好, hudi"}],
            temperature=0.2,
        )
        print("完整回复 =", full.choices[0].message.content)
        u = full.usage
        assert u is not None
        print("usage =", u.prompt_tokens, u.completion_tokens, u.total_tokens)

        cut = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好, hudi"}],
            max_tokens=4,  # 假模型按字符截；应明显比上一行短
        )
        print("截断回复 =", cut.choices[0].message.content)
        print("截断长度 =", len(cut.choices[0].message.content or ""))
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(show(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
