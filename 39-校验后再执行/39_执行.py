"""第 39 课示例：先校验，再改待办。校验失败只返回「拒绝」，不抛。

对照：@Valid 失败是 400，不是把未知方法反射出来执行。
本课一次只走「模型出工单 → run_tool」。不把结果喂回模型，所以你能单独看见列表有没有被改。
"""

from __future__ import annotations

import asyncio
import os  # 读环境变量。假模型不校验密钥。
import sys
from pathlib import Path

# 本文件在「39-校验后再执行/」。parent.parent 是仓库根，再进「38-工具调用入门」。
# 那个目录名有连字符，不能当包 import，所以把它插进搜索路径，下面才能 import mock_tools 和 todos。
_TOOLS = Path(__file__).resolve().parent.parent / "38-工具调用入门"
sys.path.insert(0, str(_TOOLS))

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs  # 假模型只填工单。tool_specs 是说明书，必须传，否则假模型只会回声。
from todos import TODOS, reset, run_tool  # TODOS 是那份内存列表本身，不是拷贝。打印它就能看见 run_tool 有没有 append。


async def once(client: AsyncOpenAI, text: str) -> None:
    """一轮：拿工单 → run_tool。不把结果喂回模型，本课先看拒绝有没有写进列表。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": text}],  # 本课不放 system。触发词都写在这句 user 里。
        tools=tool_specs(),
        temperature=0,
    )
    msg = resp.choices[0].message
    print("用户:", text)
    if not msg.tool_calls:
        # 「你好」这类才会进这里。本课 main 里的四句都会有工单，正常跑不到这一支。
        print("  无工单:", msg.content)
        return
    call = msg.tool_calls[0]  # 假模型一次一张。name 和 arguments 都在 call.function 上。
    # 执行权在 run_tool。名字不在白名单、JSON 坏了、title 空，都不会 append。
    # arguments 仍是字符串。loads 和 pydantic 都在 run_tool 里面，这里不要自己先解析。
    result = run_tool(call.function.name, call.function.arguments)
    print("  结果:", result)
    # list(TODOS) 拷出一份新列表再打印，内容是这一刻的快照。对照 new ArrayList<>(TODOS)。
    print("  当前待办:", list(TODOS))


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 没有环境变量就用占位。不要把 sk- 写进源码。
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        await once(client, "记一条 买牛奶")  # 合法标题。预期：已添加，列表里出现「买牛奶」。
        await once(client, "TOOL:BADJSON")  # arguments 不是 JSON。预期：拒绝，列表不变。
        await once(client, "TOOL:EMPTY")  # title 是空串。预期：拒绝，列表不变。
        await once(client, "TOOL:UNKNOWN")  # 工具名 drop_database。预期：白名单拒绝，列表不变。
    finally:
        await client.close()


def main() -> None:
    reset()  # 同一进程里重复跑示例时，不要把上一次的「买牛奶」留着。
    server, base_url = start_mock()  # 后台起假模型，拿到以 /v1 结尾的地址。
    try:
        asyncio.run(main_async(base_url))  # 同步入口里跑完协程。不能在 async def 里再套一层 asyncio.run。
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
