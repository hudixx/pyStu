"""第 26 课示例：官方 SDK 打本机假模型，不访问公网。

对照 Java：
- AsyncOpenAI ≈ WebClient 调支付网关
- api_key / base_url ≈ 环境变量里的密钥和渠道地址
- messages ≈ 请求体 DTO，不是魔法

想打真模型：不要改本文件。设环境变量后跑同目录 apitest.py。
"""

# 推迟注解求值：后面的 list[str]、-> None 在 import 时不会被立刻执行。
# 对照 Java：泛型/注解本来就不在运行时当代码跑。这行删掉，本文件也能跑，主要给人和 mypy 看。
from __future__ import annotations

import asyncio  # 标准库的异步运行时。本课用它把 async 函数真正跑起来。
import os  # 读环境变量。对照 System.getenv。
import sys  # 改模块搜索路径 sys.path。对照临时往 classpath 前面加一个目录。
from pathlib import Path  # 面向对象的路径。对照 java.nio.file.Path。

# 本课目录名是「26-模型SDK入门」，中间有连字符，不能写成 import 26-模型SDK入门.mock_llm
# （包名必须是合法标识符）。所以把「本文件所在目录」插到搜索路径最前面，下面才能 import mock_llm。
# __file__ = 当前这个 .py 的路径；resolve() = 变成绝对路径；parent = 它所在的文件夹。
sys.path.insert(0, str(Path(__file__).resolve().parent))

# openai 是要 pip 安装的第三方包。AsyncOpenAI 是异步客户端，方法前面都能 await。
from openai import AsyncOpenAI

# 同目录的 mock_llm.py。start_mock() 会在 127.0.0.1 上起一个假的 /v1 接口。
from mock_llm import start_mock


async def once(base_url: str) -> None:
    """一次非流式对话。base_url 指向假模型的 /v1。

    async def：函数体里可以写 await。调用 once(...) 不会马上执行完，只得到一个协程，
    要交给下面的 asyncio.run。对照：方法返回一个还没完成的 CompletableFuture，但写法是 await。
    -> None：标注「没有返回值」。对照 void。解释器默认不检查这个标注。
    """
    # 假模型不校验密钥，但 SDK 不允许 api_key 为空，所以缺环境变量时给一个占位字符串。
    # os.environ.get(名字, 默认值)：没有这个环境变量就用第二个参数。Java 的 getenv 没有默认值，要自己判 null。
    # 真密钥走 OPENAI_API_KEY，不要把 sk- 写进源码（一提交就泄密）。
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,  # 请求发到这里，而不是默认的 api.openai.com。形如 http://127.0.0.1:端口/v1
        timeout=10.0,  # 这次调用最多等 10 秒（float，单位秒）。对照 WebClient 的 responseTimeout。
        max_retries=0,  # 失败不自动重试，立刻抛异常。重试留到第 30 课。
    )
    try:
        # await：挂起这个协程，等 HTTP 回来。事件循环此时可以去干别的；这里没有别的任务，就是干等。
        # chat.completions.create 会 POST {base_url}/chat/completions，这些关键字参数就是 JSON 请求体的字段。
        resp = await client.chat.completions.create(
            model="mock-chat",  # 假模型不看这个名字；真网关必须写成对方文档里的模型 id。
            messages=[
                # 一条消息是一个 dict（对照 Map / record）。role 是谁说的，content 是原文。
                # system 定人设，user 是用户这句。列表顺序就是对话顺序。
                {"role": "system", "content": "你是助手，用中文回答。"},
                {"role": "user", "content": "你好, hudi"},
            ],
        )
        # resp 已被 SDK 解析成对象，不是原始 JSON 字符串。
        # choices 是列表：参数 n>1 时才会有多条候选。默认 1 条，取下标 0。
        # .message.content 是助手正文，类型是 str | None（只回了工具调用时可以是 None）。
        print(resp.choices[0].message.content)
    finally:
        # 成功或抛异常都要走到这里，关掉客户端内部的 httpx 连接池。
        # 对照 try-with-resources / client.close()。关闭本身是异步的，所以要 await。
        await client.close()


def main() -> None:
    # 元组拆包：函数一次返回两个值，左边用逗号接。对照 Java 只能返回一个对象，这里自带 Pair。
    # server 用来最后关掉假服务；base_url 传给上面的 once。
    server, base_url = start_mock()
    try:
        # asyncio.run：新建事件循环，把 once 这个协程跑完，再关掉循环。
        # 只能在普通同步函数里调，不能套在另一个 async def 里面。对照在 main 里 join 一个异步任务。
        asyncio.run(once(base_url))
    finally:
        # 停掉假模型的 accept 循环。不调用的话，后台线程是 daemon，主线程结束时也会被一起干掉。
        server.shutdown()


# 直接「python 26_sdk.py」时，解释器把本模块的 __name__ 设成 "__main__"，于是会调用 main()。
# 被别的文件 import 时，__name__ 是模块名，下面不执行。对照：类里的 main 不会因为被别人引用就自动跑。
if __name__ == "__main__":
    main()
