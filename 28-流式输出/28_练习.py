import asyncio
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from mock_llm import start_mock

async def stream_once(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("openai_api_key","mock-key"),
        base_url=base_url,
        timeout=10,
        max_retries=0
    )
    try:
        rest = await client.chat.completions.create(
            model="mock_model",
            messages=[
                {"role":"user", "content":"我是 hudi"}
            ],
            stream=True
        )
        prints: list[str] = []
        async for res in rest:
            if not res.choices:
                continue
            delta = res.choices[0].delta.content
            if not delta:
                continue
            print(delta, end="", flush=True)
            prints.append(delta)

        print()
        print("".join(prints))
    finally:
        await client.close()

def main() -> None:
    server , base_url = start_mock()
    try:
        asyncio.run(stream_once(base_url))
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
题2不知道，请在参考答案的注释中个给出
"""