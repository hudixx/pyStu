"""第 26 课参考答案。题 1 过：打假模型，打印「回声: 我是hudi」。

system / user、env 取 key、close、shutdown 都对。密钥没有写进文件。
user 写成「我是hudi」少了空格，假模型原样回声，不影响本课。

题 2：
- 密钥进 git 等于把支付 appKey 推进仓库。clone、日志、聊天记录都会泄露。
  对标 Spring：application.yml 用 ${OPENAI_API_KEY}，不提交生产口令；
  本地用环境变量或 IDE Run Configuration。
- 已经在 async def / FastAPI async 接口里：用 AsyncOpenAI。
  普通脚本、函数里没有 await：可以用同步 OpenAI()。
  在 async def 里用同步 OpenAI()，等于在 Netty 线程里同步调 HTTP，堵住事件循环（第 24 课）。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def send_msg(base_url: str) -> None:
    """一次非流式对话。base_url 是假模型的 /v1。"""
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[
                {"role": "system", "content": "你是助手"},
                {"role": "user", "content": "我是 hudi"},
            ],
        )
        print(resp.choices[0].message.content)
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(send_msg(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
