"""第 26 课示例：官方 SDK 打本机假模型，不访问公网。

对照 Java：
- AsyncOpenAI ≈ WebClient 调支付网关
- api_key / base_url ≈ 环境变量里的密钥和渠道地址
- messages ≈ 请求体 DTO，不是魔法
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 目录名带连字符，不能当包。把本目录插到搜索路径，才能 import mock_llm。
sys.path.insert(0, str(Path(__file__).resolve().parent))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def once(base_url: str) -> None:
    """一次非流式对话。base_url 指向假模型的 /v1。"""
    # 假模型不校验密钥，但 SDK 不允许 api_key 为空，所以给一个占位。
    # 真环境：os.environ["OPENAI_API_KEY"]，不要写死在源码里。
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,  # 本课不演示重试，失败立刻抛
    )
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",  # 假模型不看这名字；真网关要写成各家文档里的 id
            messages=[
                {"role": "system", "content": "你是助手，用中文回答。"},
                {"role": "user", "content": "你好, hudi"},
            ],
        )
        # choices 是数组：n>1 时才有多条。日常取 [0]。
        print(resp.choices[0].message.content)
    finally:
        await client.close()  # 关掉内部 httpx 连接池。对照 client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(once(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
