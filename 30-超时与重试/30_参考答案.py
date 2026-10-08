"""第 30 课参考答案。题 1 / 2 都过：打印「超时」「限流」，429-ONCE 含「回声:」。

timeout=0.3 且 max_retries=0、一直 429 用 max_retries=2、两个 client 都 close，这些对。
控制台里 mock 的 ConnectionAbortedError 是客户端 0.3 秒断开后，假模型还想写响应。
程序仍打印「超时」并正常退出，不是你的逻辑错了。

密钥名写错了：OPENAI_API_KET（少了 Y），占位写成 mock-ley。
假模型不校验密钥，所以这次能过。真网关会 401，而且读不到 OPENAI_API_KEY。

题 3：
- max_retries 对标 Resilience4j 的 Retry，不是 TimeLimiter。
  timeout= 才是 TimeLimiter / HttpClient 的超时。
- 创建订单不能照搬：聊天重试最多再生成一次、多花一份钱；
  下单重试可能真的下两单。没有幂等键就不要对有副作用的 POST 盲目重试。
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
        timeout=0.3,
        max_retries=0,
    )
    retrying = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=2,
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
