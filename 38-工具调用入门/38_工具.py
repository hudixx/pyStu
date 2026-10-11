"""第 38 课示例：看清 tool_calls 的形状。本课不执行工具。

对照：接口返回了一张还没落库的工单。打印它，不等于已经改了数据。
"""

# 推迟注解求值。后面的 -> None 这类标注在 import 时不会被执行。
from __future__ import annotations

import asyncio  # asyncio.run 把下面的 async def 真正跑起来。
import os  # 读 OPENAI_API_KEY。没有就用占位字符串。对照 System.getenv。
import sys  # 改模块搜索路径，才能 import 同目录的 mock_tools。
from pathlib import Path  # 定位「本文件所在目录」。对照 java.nio.file.Path。

# 本课目录名是「38-工具调用入门」，中间有连字符，不能写成 import 包名。
# insert(0, ...) 把本目录放到搜索路径最前。__file__ 是本 .py；resolve() 变绝对路径；parent 是文件夹。
sys.path.insert(0, str(Path(__file__).resolve().parent))  # 本目录名有连字符，不能当包名 import。

from openai import AsyncOpenAI  # 官方异步客户端。pip 安装在 venv 里，不是标准库。

# start_mock 起本机假模型。tool_specs 是交给模型的函数说明书，不是函数本身。
from mock_tools import start_mock, tool_specs


async def once(client: AsyncOpenAI, text: str) -> None:
    """问一句，只打印模型交回来的工单或正文。不调用 run_tool。

    async def：里面可以 await。调用 once(...) 得到协程，要由事件循环跑。对照还没完成的 CompletableFuture。
    -> None 对照 void。解释器默认不检查。
    """
    resp = await client.chat.completions.create(
        model="mock-chat",  # 假模型不看这个名字。真网关必须写成对方文档里的模型 id。
        messages=[
            # 一条消息是一个 dict。role 是谁说的，content 是原文。对照 Map，或一个小 DTO。
            {"role": "system", "content": "你是助手。需要数据时使用工具，不要编造待办。"},
            {"role": "user", "content": text},
        ],
        tools=tool_specs(),  # 不传这个，假模型只会回声，即使你写了「列出待办」。
        temperature=0,  # 能定住的随机性就定住。假模型不采样，这行是给以后换真模型留的。
    )
    # choices 默认只有 1 条。message 是助手这一轮的回复对象，不是原始 JSON 字符串。
    msg = resp.choices[0].message
    print("用户:", text)
    # 这一轮如果交的是工单，content 是 None。None 不是空字符串，也不是空待办列表。
    print("  content:", msg.content)  # 有工具调用时是 None。None 不是空待办列表。
    if not msg.tool_calls:
        # tool_calls 是 None 或空列表时都算假值。这一轮没有工单，函数到此结束。
        print("  tool_calls: 无")
        return
    # 假模型一次只给一张。真模型可能给多张，下标 0 只是第一张。本课先看这一张的字段。
    call = msg.tool_calls[0]
    # arguments 是 str。这里不要 json.loads，本课先看见原始形状。
    # 三个字段：函数名、参数 JSON 的原文、这张工单的 id。id 以后要和 role=tool 的 tool_call_id 对上。
    print("  工具名:", call.function.name)
    print("  arguments:", call.function.arguments)
    print("  id:", call.id)


async def main_async(base_url: str) -> None:
    """连问两句：一句会得到工单，一句只是回声。同一个 client，内部连接池复用。"""
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 假模型不校验。真密钥不要写进源码。
        base_url=base_url,  # 指到本次 start_mock 分配的 http://127.0.0.1:端口/v1。
        timeout=10.0,  # 单次 HTTP 最多等 10 秒。单位是秒，float。
        max_retries=0,  # 失败不自动重试，立刻抛。
    )
    try:
        await once(client, "列出待办")  # 假模型会交一张 list_todos 工单，arguments 是 "{}"。
        await once(client, "你好")  # 没有触发词，也没有 TOOL:，假模型只回声，没有 tool_calls。
    finally:
        await client.close()  # 关掉内部 httpx 连接池。对照 try-with-resources，关闭本身要 await。


def main() -> None:
    # 元组拆包：一个函数返回两个值。对照 Java 只能返回一个对象，这里自带 Pair。
    server, base_url = start_mock()
    try:
        # asyncio.run 新建事件循环，跑完 main_async，再关掉循环。不能套在另一个 async def 里。
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()  # 停掉假模型。后台线程是 daemon，主线程结束时也会被一起干掉。


# 直接 python 本文件时 __name__ 才是 "__main__"。被 import 时不自动起服务、不自动发问。
if __name__ == "__main__":
    main()
