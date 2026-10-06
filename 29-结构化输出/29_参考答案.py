"""第 29 课参考答案。题 1 / 2 都过：hudi、70，脏 JSON 打印「失败」。

没有失败后返回默认对象，这点对。
外层再 except ValidationError: pass 是多余的：send_msg 里已经打印并 re-raise。
from openai import api_key、from typing import Any 都没用到，删掉。
环境变量名仍应是 OPENAI_API_KEY。Windows 不区分大小写，Linux 读不到。

题 3：
- 模型说「我返回了 JSON」只是它的自称。它可能包 markdown、漏字段、类型写错、半截字符串。
  和不可信的 @RequestBody 一样，必须在边界校验。
- 这更像 @Valid DTO，不是 Jackson 裸读 Map。
  json.loads 再 data["name"] 才是 Map：缺键要到业务里才炸。
  model_validate_json 在构造时就 ValidationError。
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


class ModelDto(BaseModel):
    """接口边界。score 0～100，空 name 也不收。"""

    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


async def send_msg(client: AsyncOpenAI, msg: str) -> ModelDto:
    """合法则返回 DTO。脏 JSON 抛 ValidationError，不填默认值。"""
    res = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "system", "content": "只返回 JSON。"},
            {"role": "user", "content": msg},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = res.choices[0].message.content or ""
    return ModelDto.model_validate_json(raw)


async def run(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        dto = await send_msg(client, "hudi的分数")
        print(dto.name)
        print(dto.score)
        try:
            await send_msg(client, "TRIGGER:BADJSON")
            print("不该成功")
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
