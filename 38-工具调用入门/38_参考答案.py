"""第 38 课参考答案。题 1、题 2 都过。

运行结果：
    list_todos
    {}
    call_1
    回声: 你好

函数名写成了 mian，不是 main。下面 if 调的也是 mian，所以能跑。名字仍然是错的。
model = "mock-chat" 这种关键字参数，等号两边不要空格。

本课没有执行工具，也没有去改 TODOS。这是对的。

题 3：
- arguments 是字符串，因为协议里它就是一段 JSON 文本。对照 HTTP 正文是字节/字符串，
  不是已经装好的 DTO。要变成 dict 得你自己 json.loads，而且 loads 可能失败。
  失败留到第 39 课。SDK 不会替你变成 dict，假模型交出来的也是 "{}" 这四个字符（含花括号）。
- 模型返回 list_todos，只是填了一张工单。对照：接口收到了创建订单的请求体，行还没插入。
  假模型里没有待办列表。列表在 todos.py，要等你的代码调用 run_tool 才会变。
  本课没调用，所以列表不会因为打印了工具名就多出一条。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openai import AsyncOpenAI

from mock_tools import start_mock, tool_specs


async def once(client: AsyncOpenAI, text: str) -> None:
    """只看工单或正文。不调用 run_tool。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "system", "content": "你是助手。需要数据时使用工具，不要编造待办。"},
            {"role": "user", "content": text},
        ],
        tools=tool_specs(),  # 不传这个，「列出待办」也只会回声。
        temperature=0,
    )
    msg = resp.choices[0].message
    if not msg.tool_calls:
        # 「你好」走这里。正文以「回声:」开头。
        print(msg.content)
        return
    call = msg.tool_calls[0]
    # 三行就是题 1：名字、参数原文、工单 id。arguments 不要在本课 loads。
    print(call.function.name)
    print(call.function.arguments)
    print(call.id)


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
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
