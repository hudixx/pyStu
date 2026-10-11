"""第 42 课示例：看你已经在传的那份工具说明书。不启动 MCP 服务。

对照：先读 SPI 的接口清单，不先写一个插件容器。
MCP 是「工具怎么被发现、怎么被调用」的一种协议。本课先看你已经有的那份 JSON，不引入新框架。
"""

from __future__ import annotations

import asyncio
import json  # dumps 把说明书打成缩进过的 JSON，方便对着字段看。
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))  # 才能 import mock_tools。目录名有连字符，不能当包。

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs


def main_print_specs() -> None:
    """说明书是普通 list[dict]，谁都能打印。没有框架也能有契约。"""
    specs = tool_specs()  # 每次调用新建一份。这里还没发 HTTP。
    # 列表推导：从每份说明书里取出 function.name。对照 stream.map(item -> item.getFunction().getName()).toList()。
    names = [item["function"]["name"] for item in specs]
    print("工具名:", ",".join(names))
    # indent=2 方便对照 JSON Schema。这不是 MCP 的线缆格式，只是同一份契约的一种写法。
    # ensure_ascii=False：中文说明保持原样。
    print(json.dumps(specs, ensure_ascii=False, indent=2))


async def echo(client: AsyncOpenAI, with_tools: bool) -> None:
    """ECHO-TOOLS 让假模型把「它实际收到的工具名」说出来。不传 tools 时应得到「没有」。

    with_tools 是普通参数。调用时写成 echo(client, with_tools=True) 更清楚，按位置传 True 也可以。
    """
    # 先装进 dict，是因为 tools 这个键可有可无。不能在 create(...) 里写两个几乎相同的调用再复制粘贴。
    kwargs: dict = {
        "model": "mock-chat",
        "messages": [{"role": "user", "content": "TOOL:ECHO-TOOLS"}],
        "temperature": 0,
    }
    if with_tools:
        kwargs["tools"] = tool_specs()  # 键名必须是 tools，和 create 的参数名一致。下一行 ** 会按这个名字传进去。
    # **kwargs 把字典拆成关键字参数。对照把一个 Map 展开成方法的各个形参，而不是把整张 Map 当一个参数传。
    # 写成 create(kwargs) 是错的：那是一个位置参数，形参对不上。
    resp = await client.chat.completions.create(**kwargs)
    # 三元表达式。真值 if 条件 else 假值。对照 条件 ? "带说明书" : "不带说明书"。
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
        await echo(client, with_tools=True)  # 假模型应原样列出 list_todos,add_todo。名字来自请求，不是它自己编的。
        await echo(client, with_tools=False)  # 应回答「工具清单: （没有）」。没传说明书就不能假装有工具。
    finally:
        await client.close()


def main() -> None:
    main_print_specs()  # 先在本地把契约打出来。这一步不需要假模型，也不需要网络。
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))  # 再让假模型承认它收到了什么。两步对得上，说明书才算真的送上去了。
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
