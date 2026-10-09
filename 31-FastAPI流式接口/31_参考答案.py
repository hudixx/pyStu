"""第 31 课参考答案。题 1 / 2 都过。

POST /chat 200，正文「回声: 我是 hudi」。
POST /extract 合法 200，name=hudi、score=70。
TRIGGER:BADJSON 是 422，没有 200 空对象。
timeout、环境变量密钥、delta 为空就跳过，都对。

从 starlette 导入 StreamingResponse / TestClient 能跑。
FastAPI 再导出的是同一套，作业里写成 fastapi 更整齐。

_client 的默认 base_url 写死了 127.0.0.1:8001。
这次 main 先改了环境变量再打请求，所以没用到默认值。
别人没设 OPENAI_BASE_URL 时会去打一个没人听的端口。默认用 None，缺了就报错。

题 3：
- StreamingResponse 对标 Spring WebFlux 的 Flux<String>，或 SseEmitter。
  不是等完整 body 的 ResponseEntity<String>。
- 脏 JSON 不能 200 空对象：调用方会当成成功写库。
  校验失败应是 422，和 Bean Validation 失败同一个状态码。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from mock_llm import start_mock

app = FastAPI(title="第 31 课参考答案")


class ChatIn(BaseModel):
    text: str = Field(min_length=1)


class Person(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


def _client() -> AsyncOpenAI:
    """请求时再读环境变量。main 必须先写入 OPENAI_BASE_URL。"""
    base = os.environ.get("OPENAI_BASE_URL")
    if not base:
        raise RuntimeError("先设置 OPENAI_BASE_URL，不要写死 8001")
    return AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base,
        timeout=10.0,
        max_retries=0,
    )


@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    async def chunks():
        client = _client()
        try:
            stream = await client.chat.completions.create(
                model="mock-chat",
                messages=[{"role": "user", "content": body.text}],
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                piece = chunk.choices[0].delta.content
                if piece:
                    yield piece
        finally:
            await client.close()

    return StreamingResponse(chunks(), media_type="text/plain; charset=utf-8")


@app.post("/extract")
async def extract(body: ChatIn) -> Person:
    client = _client()
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[
                {"role": "system", "content": "只返回 JSON。"},
                {"role": "user", "content": body.text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        raw = resp.choices[0].message.content or ""
        try:
            return Person.model_validate_json(raw)
        except ValidationError:
            raise HTTPException(status_code=422, detail="模型没有返回合法 JSON")
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ.setdefault("OPENAI_API_KEY", "mock-key")
    try:
        client = TestClient(app)
        streamed = client.post("/chat", json={"text": "我是 hudi"})
        print("/chat", streamed.status_code, streamed.text)
        ok = client.post("/extract", json={"text": "抽取"})
        print("/extract", ok.status_code, ok.json())
        bad = client.post("/extract", json={"text": "TRIGGER:BADJSON"})
        print("/extract 脏 JSON", bad.status_code)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
