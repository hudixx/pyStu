from __future__ import annotations

import sys
from pathlib import Path
import os
import asyncio
import json

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))
from openai import AsyncOpenAI
from mock_tools import start_mock, tool_specs

def main_print_specs() -> None:
    spect = tool_specs()
    names = [ item["function"]["name"] for item in spect]
    print("工具名", ",".join(names))
    print(json.dumps(spect, indent=2, ensure_ascii=False))

async def echo(client: AsyncOpenAI, with_tools: bool) -> None:
    kwargs: dict =  {
        "model": "mock-chat",
        "messages": [{"role": "user", "content": "TOOL:ECHO-TOOLS"}],
        "temperature": 0,
    }
    if with_tools:
        kwargs["tools"] = tool_specs()
    resp = await client.chat.completions.create(**kwargs)
    label = "带说明书" if with_tools else "不带说明书"
    print(label, "->", resp.choices[0].message.content)

async def main_asyn(base_url: str) -> None:
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
        asyncio.run(main_asyn(base_url))
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()
"""
 题3不知道，请在参考答案的注释中个给出
"""