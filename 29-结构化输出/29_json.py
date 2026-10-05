"""第 29 课示例：json_object + pydantic；脏 JSON 必须失败。

对照：@RequestBody + Bean Validation。模型比用户更容易违规。
response_format 只是「请模型吐 JSON」的请求字段，假模型会因此回一段合法 JSON；
它不是校验器。校验发生在我们自己的 Person.model_validate_json。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 让本目录的上一级里的「26-模型SDK入门」出现在模块搜索路径中，才能 import mock_llm。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI
# BaseModel：pydantic 的 DTO 基类。Field：字段约束。ValidationError：校验失败时抛的异常。
# 对照：一个带 Bean Validation 注解的类，加上 BindException 那一类校验异常。
from pydantic import BaseModel, Field, ValidationError

from mock_llm import start_mock


class Person(BaseModel):
    """接口边界 DTO。score 限制在 0～100，和业务规则写在类型上。

    继承 BaseModel 之后，构造和 model_validate_json 都会真的校验、并做类型转换。
    对照第 17 课：它像 Jackson + Bean Validation，不是「只给 IDE 看的注解」。
    """

    name: str = Field(min_length=1)  # 至少 1 个字符。空串会被拒绝。
    score: int = Field(ge=0, le=100)  # ge = greater or equal，le = less or equal。对照 @Min(0) @Max(100)。


async def extract(client: AsyncOpenAI, user_text: str) -> Person:
    """成功返回 Person；JSON 脏了或字段不合规则就抛 ValidationError。调用方不在这里抓。"""
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[
            {"role": "system", "content": "只返回 JSON。"},  # 给人设一句。假模型其实不读这句话，它看 response_format。
            {"role": "user", "content": user_text},
        ],
        # 请求体字段，不是 Python 语法。type=json_object 时，假模型走 _make_reply 的 JSON 分支。
        # 真模型也只是「尽量」吐 JSON，仍可能吐歪，所以下面还要自己校验。
        response_format={"type": "json_object"},
        temperature=0,  # 抽取任务希望稳定。假模型不随机，这个值不会改变那句固定 JSON。
    )
    # content 可能是 None。or "" 让后面一定拿到 str。对照 Objects.toString 之前先判空。
    raw = resp.choices[0].message.content or ""
    # 解析 JSON 并按 Person 的字段约束校验。失败抛 ValidationError（脏 JSON、缺字段、score 超范围都会）。
    # 对照：objectMapper.readValue(raw, Person.class)，再跑一遍 Validator。
    return Person.model_validate_json(raw)


async def run(base_url: str) -> None:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    try:
        # 假模型看到 json_object，回 {"name": "hudi", "score": 70}，能通过 Person 的约束。
        ok = await extract(client, "抽取 hudi 的分数")
        # print 对象时会走 pydantic 模型的字符串形式，能看见 name 和 score 两个字段。
        print("成功 =", ok)

        try:
            # 用户文案含 TRIGGER:BADJSON 时，假模型改回「{name: hudi, score: 70」这种缺引号的文本。
            await extract(client, "TRIGGER:BADJSON")
            print("不该走到这里")  # model_validate_json 正常的话会抛，这条不该执行。
        except ValidationError as e:
            # as e：把异常对象接住。对照 catch (ValidationException e)。
            # error_count()：这次校验有几条错误。脏 JSON 通常是 1 条「根本不是合法 JSON」。
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
