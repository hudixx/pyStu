import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


from openai import AsyncOpenAI
from mock_llm import start_mock

async def send_msg(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY","mock-key"),
        base_url= base_url,
        timeout=10,
        max_retries=0
    )
    try:

        resp = await client.chat.completions.create(
            model ="mock-chat",
            messages =[
                {"role": "system", "content": "你是助手"},
                {"role": "user", "content": "我是 hudi"}
            ]
        )
        print(resp.choices[0].message.content)
    finally:
        await client.close()

def main() -> None:
    server , base_url = start_mock()
    try:
        asyncio.run(send_msg(base_url))
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
题2
    请在参考答案的注释只能给出
"""
