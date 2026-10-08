import asyncio
import sys
import os
from pathlib import Path

from openai import AsyncOpenAI, APITimeoutError, RateLimitError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))


from mock_llm import start_mock

async def call(client: AsyncOpenAI, text: str) -> str:
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return resp.choices[0].message.content or ""

async def run(base_url: str) -> None:
    short = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KET", "mock-ley"),
        base_url=base_url,
        timeout=0.3,
        max_retries=0
    )
    retrying = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-ley"),
        base_url=base_url,
        timeout=10,
        max_retries=2
    )

    try:
        try:
            await call(short, "TRIGGER:SLOW")
            print("慢请求不该成功")
        except APITimeoutError:
            print("超时")

        try:
            await call(retrying, "TRIGGER:429")
            print("一直 429 不该成功")
        except RateLimitError:
            print("限流")

        text = await call(retrying, "TRIGGER:429-ONCE")
        print("重试成功 =", text)
    finally:
        await short.close()
        await retrying.close()

def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(run(base_url))
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
题3不知道，请在参考答案的注释中个给出
"""
