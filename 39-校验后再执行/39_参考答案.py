"""第 39 课参考答案。题 1、题 2 都过。

运行结果：
    记一条 买牛奶 → 已添加 买牛奶，列表 ['买牛奶']
    TOOL:BADJSON → 拒绝: 参数不是 JSON，列表不变
    TOOL:EMPTY   → 拒绝: title 不合法，列表不变
    TOOL:UNKNOWN → 拒绝: 未知工具 drop_database，列表不变

你的 list_todos 三个 if 最后都会 return，这次不会掉进 AddTodo。能跑，但读起来像没分清两个工具。
白名单写成了 list，用元组更合适。逗号后面补一个空格。
AddTodo 没有 extra=forbid。多出来的字段 pydantic 默认会丢掉，校验仍通过。
练习没考这个，所以不算错。下面这份把多字段也拒绝。

题 3：
- 工具名是不可信输入，和 URL 一样。不能 getattr(模块, name)()。
  模型若给出 drop_database，反射会去找那个函数。白名单只放行 list_todos 和 add_todo，
  未知名字连 JSON 都不解析。对照不要 Class.forName(用户给的类名)。
- 校验失败要 return 一段文字，不要把 ValidationError 抛出循环。
  下一课这段文字会作为 role=tool 喂回模型。抛出去循环会炸，模型看不到「你拒绝了」，
  可能当成这张工单已经成功。对照：@Valid 失败转成 400 的响应体，不是把栈打到调用方脸上。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))

from mock_tools import start_mock, tool_specs

TODOS: list[str] = []


class AddTodo(BaseModel):
    """多一个未知字段就失败。默认 ignore 会把脏字段悄悄丢掉。"""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=40)


def run_tool(name: str, arguments: str) -> str:
    """永远返回字符串。拒绝的分支都在 append 之前 return。"""
    if name not in ("list_todos", "add_todo"):
        return f"拒绝: 未知工具 {name}"
    try:
        raw = json.loads(arguments)
    except json.JSONDecodeError:
        return "拒绝: 参数不是 JSON"
    if name == "list_todos":
        # 这个工具在这里就结束。不要落到下面的 AddTodo。
        if raw != {}:
            return "拒绝: 参数应为空对象"
        if not TODOS:
            return "待办为空"
        return "、".join(TODOS)
    try:
        item = AddTodo.model_validate(raw)
    except ValidationError:
        return "拒绝: title 不合法"
    TODOS.append(item.title)
    return f"已添加 {item.title}"


async def once(client: AsyncOpenAI, text: str) -> None:
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
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
