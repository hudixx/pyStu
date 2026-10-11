"""第 38 课示例：看清 tool_calls 的形状。本课不执行工具。

对照：接口返回了一张还没落库的工单。打印它，不等于已经改了数据。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 本目录名有连字符，不能当包名 import。

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs


async def once(client: AsyncOpenAI, text: str) -> None:
    """问一句，只打印模型交回来的工单或正文。不调用 run_tool。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "system", "content": "你是助手。需要数据时使用工具，不要编造待办。"},
            {"role": "user", "content": text},
        ],
        tools=tool_specs(),  # 不传这个，假模型只会回声，即使你写了「列出待办」。
        temperature=0,
    )
    msg = resp.choices[0].message
    print("用户:", text)
    print("  content:", msg.content)  # 有工具调用时是 None。None 不是空待办列表。
    if not msg.tool_calls:
        print("  tool_calls: 无")
        return
    call = msg.tool_calls[0]
    # arguments 是 str。这里不要 json.loads，本课先看见原始形状。
    print("  工具名:", call.function.name)
    print("  arguments:", call.function.arguments)
    print("  id:", call.id)


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 假模型不校验。真密钥不要写进源码。
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        await once(client, "列出待办")
        await once(client, "你好")
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
