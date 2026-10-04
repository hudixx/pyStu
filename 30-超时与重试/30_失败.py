"""第 30 课示例：超时、一直 429、429 一次后重试成功。

对照 Resilience4j：TimeLimiter + Retry，错误码换成网关的。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import APITimeoutError, AsyncOpenAI, RateLimitError

from mock_llm import start_mock


async def call(client: AsyncOpenAI, text: str) -> str:
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": text}],
    )
    return resp.choices[0].message.content or ""


async def run(base_url: str) -> None:
    short = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=0.3,  # 假模型 SLOW 会睡 2 秒
        max_retries=0,
    )
    retrying = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=2,  # 429-ONCE：第一次失败，第二次应成功
    )
    try:
        try:
            await call(short, "TRIGGER:SLOW")
            print("慢请求不该成功")
        except APITimeoutError:
            print("超时：TRIGGER:SLOW 被 timeout=0.3 拦住")

        try:
            await call(retrying, "TRIGGER:429")
            print("一直 429 不该成功")
        except RateLimitError:
            print("限流：TRIGGER:429 重试耗尽")

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
