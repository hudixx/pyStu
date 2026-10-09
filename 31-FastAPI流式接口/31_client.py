import os

from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from starlette.responses import StreamingResponse

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("31_client:app", host="127.0.0.1", port=8000, reload=True)