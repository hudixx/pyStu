"""第 42 课参考答案。题 1、题 2 都过。

带说明书：工具清单: list_todos,add_todo
不带说明书：工具清单: （没有）
没有安装 MCP，也没有起服务。

变量名 spect、函数名 main_asyn 不影响结果。名字仍然写错了。

题 3：
- 这次 HTTP 里的 tools，是你在同一次请求里亲手带上的说明书，函数在你这个进程里执行。
  MCP 是另一个进程公布清单（list_tools），宿主再调用它（call_tool）。常见传输是 stdio。
  两边的契约都是名字、说明、JSON Schema。差在谁发现、谁执行，不在说明书长什么样。
  对照：现在是 Spring 进程直接调自己的 Service。MCP 像把 Service 用 SPI 暴露给进程外的宿主。
- 第 40 课的循环已经能看见步数和系统提示。Agent 框架把循环藏进库里，
  上限被谁改掉要再翻一层。组里还没用某个框架时，不先装它。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))

from mock_tools import start_mock, tool_specs


async def echo(client: AsyncOpenAI, with_tools: bool) -> None:
    """ECHO-TOOLS 只复述这次请求里真正送到的工具名。"""
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
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
