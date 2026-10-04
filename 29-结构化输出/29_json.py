"""第 29 课示例：json_object + pydantic；脏 JSON 必须失败。

对照：@RequestBody + Bean Validation。模型比用户更容易违规。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from mock_llm import start_mock


class Person(BaseModel):
    """接口边界 DTO。score 限制在 0～100，和业务规则写在类型上。"""

    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


async def extract(client: AsyncOpenAI, user_text: str) -> Person:
    """成功返回 Person；JSON 脏了就抛 ValidationError。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "system", "content": "只返回 JSON。"},
            {"role": "user", "content": user_text},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = resp.choices[0].message.content or ""
    return Person.model_validate_json(raw)


async def run(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        ok = await extract(client, "抽取 hudi 的分数")
        print("成功 =", ok)

        try:
            await extract(client, "TRIGGER:BADJSON")
            print("不该走到这里")
        except ValidationError as e:
            print("脏 JSON 被拦住:", e.error_count(), "个错误")
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
