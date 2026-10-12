import asyncio
import os

from openai import AsyncOpenAI
from mock_tools import start_mock, tool_specs

async def once(client: AsyncOpenAI, text: str) -> None:
    resp = await client.chat.completions.create(
        model = "mock-chat",
        messages = [
            {"role": "system", "content": "你是助手。需要数据时使用工具，不要编造待办。"},
            {"role": "user", "content": text},
        ],
        tools=tool_specs(),
        temperature=0
    )
    msg = resp.choices[0].message
    if not msg.tool_calls:
        print(msg.content)
        return
    call = msg.tool_calls[0]
    print(call.function.name)
    print(call.function.arguments)
    print(call.id)


async def main_async(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 假模型不校验。真密钥不要写进源码。
        base_url=base_url,  # 指到本次 start_mock 分配的 http://127.0.0.1:端口/v1。
        timeout=10.0,  # 单次 HTTP 最多等 10 秒。单位是秒，float。
        max_retries=0 # 失败不自动重试，立刻抛。
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

if __name__ == '__main__':
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""