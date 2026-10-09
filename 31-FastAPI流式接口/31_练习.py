import os
import sys

from pathlib import Path
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from mock_llm import start_mock

app = FastAPI(title="第31课测试")

class ChatIn(BaseModel):
    text: str = Field(min_length=1)

class Person(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0,le=100)

def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY","mock-key"),
        base_url=os.environ.get("OPENAI_BASE_URL","http://127.0.0.1:8001/v1"),
        timeout=10.0,
        max_retries=0
    )

@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    async def chunks():
        client = _client()
        try:
            stream = await client.chat.completions.create(
                model="mock-chat",
                messages=[
                    {"role": "user", "content": body.text}
                ],
                stream=True
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
                {"role": "system", "content": "只返回json"},
                {"role": "user", "content": body.text}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        raw = resp.choices[0].message.content or ""
        try:
            return Person.model_validate_json(raw)
        except ValidationError:
            raise HTTPException(status_code = 422, detail = "模型没有返回合法 JSON")
    finally:
        await client.close()


def main() -> None:
    server , base_url = start_mock()
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ.setdefault("OPENAI_API_KEY", "mock-key")
    try:
        client = TestClient(app)
        streamed = client.post("/chat",  json={"text": "我是 hudi"})
        print("status_code == ", streamed.status_code, "。", streamed.text)
        ok = client.post("/extract", json={"text": "hudi的分数"})
        print("status_code == ", ok.status_code, ok.json())
        bad = client.post("/extract", json = {"text": "TRIGGER:BADJSON"})
        print("status_code == ", bad.status_code)

    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
题3不知道，请在参考答案的注释中个给出
"""