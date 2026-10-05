"""第 27 课参考答案。usage 相加对，max_tokens=5 截成 5 个字符也对。

你写成 Path(__name__) 而不是 Path(__file__)。
直接运行时 __name__ 是 "__main__"，路径跟着当前目录走：
在本课目录里跑能找到 mock_llm，在仓库根目录跑会 ModuleNotFoundError。
对照：不要用 Class.getName() 去拼文件路径，要用本文件的位置。

另外两次请求后没有 await client.close()。第 26 课已经有 finally。

题 3：
- 整库拼进 prompt：输入 token 暴涨，账单按 prompt_tokens 计；
  模型要先读完这些字才开始生成，延迟也变长。上下文装不下还会直接失败。
  「理解变差」是后果之一，但题目问的是钱和延迟。
- max_tokens 限制的是输出，不是输入。输入看 messages 有多长。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def send_test(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        full = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "我是 hudi"}],
        )
        print(full.choices[0].message.content)
        usage = full.usage
        assert usage is not None
        print(usage.prompt_tokens, usage.completion_tokens, usage.total_tokens)

        cut = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "我是 hudi"}],
            max_tokens=5,
        )
        content = cut.choices[0].message.content or ""
        print(content)
        print(len(content))
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(send_test(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
