"""第 39 课示例：先校验，再改待办。校验失败只返回「拒绝」，不抛。

对照：@Valid 失败是 400，不是把未知方法反射出来执行。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs
from todos import TODOS, reset, run_tool


async def once(client: AsyncOpenAI, text: str) -> None:
    """一轮：拿工单 → run_tool。不把结果喂回模型，本课先看拒绝有没有写进列表。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": text}],
        tools=tool_specs(),
        temperature=0,
    )
    msg = resp.choices[0].message
    print("用户:", text)
    if not msg.tool_calls:
        print("  无工单:", msg.content)
        return
    call = msg.tool_calls[0]
    # 执行权在 run_tool。名字不在白名单、JSON 坏了、title 空，都不会 append。
    result = run_tool(call.function.name, call.function.arguments)
    print("  结果:", result)
    print("  当前待办:", list(TODOS))


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        await once(client, "记一条 买牛奶")
        await once(client, "TOOL:BADJSON")
        await once(client, "TOOL:EMPTY")
        await once(client, "TOOL:UNKNOWN")
    finally:
        await client.close()


def main() -> None:
    reset()  # 同一进程里重复跑示例时，不要把上一次的「买牛奶」留着。
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
