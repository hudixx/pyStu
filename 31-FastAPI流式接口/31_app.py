"""第 31 课示例：FastAPI 流式 /chat + JSON /extract。默认打假模型。

对照 Spring：
- StreamingResponse ≈ Flux / SSE
- /extract 的 pydantic ≈ @Valid DTO；脏 JSON → 422
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

app = FastAPI(title="第 31 课演示")


class ChatIn(BaseModel):
    text: str = Field(min_length=1)


class Person(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


def _client() -> AsyncOpenAI:
    """每次请求建也行；练习里允许模块级单例。timeout 必写。"""
    base = os.environ.get("OPENAI_BASE_URL")
    return AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base,
        timeout=10.0,
        max_retries=0,
    )


@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    """流式把模型增量吐给调用方。media_type 用纯文本，少一层 SSE 概念。"""

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
    """成功返回 Person；模型胡言 422。"""
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
    """起假模型 → TestClient 打两个接口 → 退出。不必手动 uvicorn。"""
    server, base_url = start_mock()
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ.setdefault("OPENAI_API_KEY", "mock-key")
    try:
        client = TestClient(app)
        streamed = client.post("/chat", json={"text": "你好, hudi"})
        print("GET 不是这个接口；POST /chat =", streamed.status_code, streamed.text)

        ok = client.post("/extract", json={"text": "抽取"})
        print("POST /extract 合法 =", ok.status_code, ok.json())

        bad = client.post("/extract", json={"text": "TRIGGER:BADJSON"})
        print("POST /extract 脏 JSON =", bad.status_code)
    finally:
        server.shutdown()


if __name__ == "__main__":
    # TestClient 内部会跑事件循环；不要再 asyncio.run 包一层。
    main()
    # 若想看 /docs：先 start_mock 并 export OPENAI_BASE_URL，再
    #   cd 31-FastAPI流式接口
    #   python -m uvicorn 31_app:app --port 8000
    # 目录名带连字符，uvicorn 的 31_app:app 必须在本目录执行。
