import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from mock_llm import start_mock

from openai import AsyncOpenAI

async def send_test(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key= os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10,
        max_retries=0
    )
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[
                {"role": "user","content": "我是 hudi"}
            ]
        )
        usage = resp.usage
        content = resp.choices[0].message.content
        assert usage is not None
        assert content is not None
        print(content)
        print(usage.prompt_tokens)
        print(usage.completion_tokens)
        print(usage.total_tokens)

        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[
                {"role": "user","content": "我是 hudi"}
            ],
            max_tokens=5
        )
        content = resp.choices[0].message.content
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

"""
题3：
    因为模型上下文长度有限，prompt过长，是模型上下文理解失效，并且理解越难。
    max_tokens 限制的是输出
"""