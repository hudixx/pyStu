import os
import sys
import asyncio
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI, api_key
from pydantic import BaseModel, Field, ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from mock_llm import start_mock

class ModelDto(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0,le=100)


async def send_msg(client: AsyncOpenAI, msg: str) -> ModelDto:
    res = await client.chat.completions.create(
        model="mock-chat",
        messages= [
            {"role": "system", "content": "请返回json格式"},
            {"role": "user", "content": msg}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    rest = res.choices[0].message.content or ""
    return ModelDto.model_validate_json(rest)

async def run(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("openai_api_key", "mock-key"),
        base_url=base_url,
        timeout=10,
        max_retries=0
    )
    try:
        dto = await send_msg(client, "hudi的分数")
        print(dto.name)
        print(dto.score)
        try:
            await send_msg(client, "TRIGGER:BADJSON")
        except ValidationError:
            print("失败")
    finally:
        await client.close()

def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(run(base_url))
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
题3不知道，请在参考答案的注释中个给出
"""