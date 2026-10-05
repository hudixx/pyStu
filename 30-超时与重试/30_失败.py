"""第 30 课示例：超时、一直 429、429 一次后重试成功。

对照 Resilience4j：TimeLimiter + Retry，错误码换成网关的。
这里没有自己写重试循环。重试是 AsyncOpenAI(max_retries=...) 内部做的：
遇到 429 会再 POST 一次，次数用完仍是 429，才把 RateLimitError 抛给你。

假模型约定（写在用户消息里）：
- TRIGGER:SLOW      先睡 2 秒
- TRIGGER:429       每次都 429
- TRIGGER:429-ONCE  奇数次 429、偶数次成功（第 1 次失败，第 2 次成功）
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

# APITimeoutError：在 timeout 内没拿到响应。RateLimitError：HTTP 429。
# 都是 openai 包里的异常类。对照自己定义的业务异常，用类型区分，而不是看 message 字符串。
from openai import APITimeoutError, AsyncOpenAI, RateLimitError

from mock_llm import start_mock


async def call(client: AsyncOpenAI, text: str) -> str:
    """发一句用户消息，返回助手正文。失败时异常原样往外抛，这里不抓。

    -> str：标注返回字符串。content 为 None 时用 or "" 收成空串，保证真的是 str。
    """
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": text}],  # text 里的 TRIGGER:... 是说给假模型看的开关。
    )
    return resp.choices[0].message.content or ""


async def run(base_url: str) -> None:
    # 两个客户端，同一台假模型，策略不同。对照两个配了不同 TimeLimiter / Retry 的 WebClient。
    short = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=0.3,  # 只等 0.3 秒。假模型 SLOW 会睡 2 秒，所以这次应当超时。
        max_retries=0,  # 超时不要再重试，否则你会以为「超时没生效」，其实是在重试。
    )
    retrying = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,  # 给够时间，这个客户端用来看 429，不看超时。
        max_retries=2,  # 失败后最多再试 2 次（一共最多 3 次 POST）。429-ONCE 第 2 次就会成功。
    )
    try:
        try:
            await call(short, "TRIGGER:SLOW")
            print("慢请求不该成功")  # 若打印出来，说明超时没拦住，和本课预期相反。
        except APITimeoutError:
            # 只抓超时。别的异常（比如连不上）不会被这里吞掉，会继续往外抛。
            print("超时：TRIGGER:SLOW 被 timeout=0.3 拦住")

        try:
            # 每次都 429。max_retries=2 会多打两次，三次都是 429，然后抛 RateLimitError。
            await call(retrying, "TRIGGER:429")
            print("一直 429 不该成功")
        except RateLimitError:
            print("限流：TRIGGER:429 重试耗尽")

        # 不包 try：按假模型的计数，第 1 次 429，SDK 自动再请求，第 2 次成功，这里应当拿到正文。
        # 注意 _once_hits 是假模型进程里的共享计数。若上面「一直 429」的路径没有碰到 429-ONCE，计数从 0 开始。
        text = await call(retrying, "TRIGGER:429-ONCE")
        print("重试成功 =", text)
    finally:
        # 两个客户端各自有连接池，都要关。对照两个 Closeable 都要在 finally 里 close。
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
