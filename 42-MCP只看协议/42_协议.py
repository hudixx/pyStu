"""第 42 课示例：看你已经在传的那份工具说明书。不启动 MCP 服务。

对照：先读 SPI 的接口清单，不先写一个插件容器。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs


def main_print_specs() -> None:
    """说明书是普通 list[dict]，谁都能打印。没有框架也能有契约。"""
    specs = tool_specs()
    names = [item["function"]["name"] for item in specs]
    print("工具名:", ",".join(names))
    # indent=2 方便对照 JSON Schema。这不是 MCP 的线缆格式，只是同一份契约的一种写法。
    print(json.dumps(specs, ensure_ascii=False, indent=2))


async def echo(client: AsyncOpenAI, with_tools: bool) -> None:
    """ECHO-TOOLS 让假模型把「它实际收到的工具名」说出来。不传 tools 时应得到「没有」。"""
    kwargs: dict = {
        "model": "mock-chat",
        "messages": [{"role": "user", "content": "TOOL:ECHO-TOOLS"}],
        "temperature": 0,
    }
    if with_tools:
        kwargs["tools"] = tool_specs()
    resp = await client.chat.completions.create(**kwargs)
    label = "带说明书" if with_tools else "不带说明书"
    print(label, "→", resp.choices[0].message.content)


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        await echo(client, with_tools=True)
        await echo(client, with_tools=False)
    finally:
        await client.close()


def main() -> None:
    main_print_specs()
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
