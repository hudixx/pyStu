from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

TODOS: list[str] = []

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"

sys.path.insert(0, str(_TOOLS))

from mock_tools import start_mock, tool_specs

class AddTodo(BaseModel):
    title: str = Field(min_length=1)

def run_tool(name: str, arguments: str) -> str:
    if name not in ["list_todos","add_todo"]:
        return f"拒绝: 未知工具 {name}"
    try:
        raw = json.loads(arguments)
    except json.JSONDecodeError:
        return "拒绝: 参数不是json"
    if name == "list_todos":
        if raw == {} and TODOS:
            return "、".join(TODOS)
        if raw != {}:
            return "拒绝: 参数应为空对象"
        if not TODOS:
            return "待办为空"
    try:
        item = AddTodo.model_validate(raw)
    except ValidationError:
        return  "拒绝: title 不合法"
    TODOS.append(item.title)
    return f"已添加 {item.title}"

async def once(client: AsyncOpenAI, text: str) -> None:
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": text}],
        tools=tool_specs(),
        temperature=0
    )
    msg = resp.choices[0].message
    print("用户:", text)
    if not msg.tool_calls:
        print("  无工具调用：", msg.content)
        return
    call = msg.tool_calls[0]
    result = run_tool(call.function.name, call.function.arguments)
    print("  结果:", result)
    print("  当前待办:", list(TODOS))

async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY","mock-key"),
        base_url=base_url,
        timeout=10,
        max_retries=0
    )
    try:
        await once(client, "记一条 买牛奶")
        await once(client, "TOOL:BADJSON")
        await once(client, "TOOL:EMPTY")
        await once(client, "TOOL:UNKNOWN")
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

"""
 题3不知道，请在参考答案的注释中个给出
"""