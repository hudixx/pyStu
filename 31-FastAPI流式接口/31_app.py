"""第 31 课示例：FastAPI 流式 /chat + JSON /extract。默认打假模型。

对照 Spring：
- StreamingResponse ≈ Flux / SSE（这里 media_type 用的是纯文本，不是 text/event-stream）
- /extract 的 pydantic ≈ @Valid DTO；脏 JSON → 422

直接 python 本文件时，不会 listen 端口，而是用 TestClient 在进程内打自己的两个接口。
对照 MockMvc：不占用 8000，请求直接进 app。
"""

from __future__ import annotations

import os  # 读/写 OPENAI_BASE_URL，让路由里的客户端知道假模型地址。
import sys
from pathlib import Path

# mock_llm.py 不在本目录，在仓库根下的「26-模型SDK入门」。插进搜索路径才能 import。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from fastapi import FastAPI, HTTPException  # HTTPException：在路由里主动返回某个状态码。对照 ResponseStatusException。
from fastapi.responses import StreamingResponse  # 返回一个「还会继续往外 yield」的响应体。
from fastapi.testclient import TestClient  # 进程内假客户端。对照 MockMvc。
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from mock_llm import start_mock

# 创建应用对象。title 会出现在自动生成的 /docs 里。这行在 import 时就执行，全进程一份。
app = FastAPI(title="第 31 课演示")


class ChatIn(BaseModel):
    """POST 的请求体。JSON 字段名就是 text。对照一个只有一个字段的 @RequestBody DTO。"""

    text: str = Field(min_length=1)  # 缺字段、或 ""，FastAPI 在进路由函数之前就回 422，函数体不会跑。


class Person(BaseModel):
    """/extract 的响应体。FastAPI 看到返回类型是 BaseModel，会把它序列化成 JSON。"""

    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)  # 0～100。对照 @Min @Max。


def _client() -> AsyncOpenAI:
    """每次请求建一个客户端也行；练习里允许改成模块级单例。timeout 必写，避免假模型卡住时无限等。

    普通 def，不是 async def：这里只是构造对象，没有 await。对照 new WebClient.Builder()...build()。
    """
    # 地址不写死。main() 里会把假模型的 base_url 放进这个环境变量。没设置时 base 是 None，SDK 会走它的默认官网。
    base = os.environ.get("OPENAI_BASE_URL")
    return AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base,
        timeout=10.0,
        max_retries=0,  # 演示接口不把重试藏起来。要重试看第 30 课。
    )


@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    """流式把模型增量吐给调用方。media_type 用纯文本，少一层 SSE 概念。

    装饰器 @app.post 把这个函数注册成 POST /chat。对照 @PostMapping("/chat")。
    body 由 FastAPI 按 ChatIn 从 JSON 里解析并校验，你不用自己 request.getReader()。
    """

    async def chunks():
        """异步生成器：每 yield 一次，就往响应里推一小段字符串。对照 Flux.create 里的 sink.next。

        它定义在 chat 里面，所以能直接用外层的 body。这叫闭包。对照匿名内部类抓外面的局部变量，
        但这里的 body 不需要是 final。
        """
        client = _client()
        try:
            stream = await client.chat.completions.create(
                model="mock-chat",
                messages=[{"role": "user", "content": body.text}],  # 用调用方传来的 text，不是写死的句子。
                stream=True,  # 向假模型要 SSE。假模型一个字一块。
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue  # 空 choices（例如结束前的 usage 块）跳过。
                piece = chunk.choices[0].delta.content  # 这一小块的增量文本，可能是 None。
                if piece:
                    # yield 把这段交给 StreamingResponse，然后挂起，等它要下一段再回来。
                    # 不是 return：return 会结束整个生成器。对照 sink.next(piece) 而不是结束流。
                    yield piece
        finally:
            await client.close()  # 流正常结束或中途出错，都关连接池。

    # chunks() 加上括号：立刻得到异步生成器对象，但函数体要等响应开始消费才跑。
    # 不写括号的话，传进去的是函数本身，不是生成器。
    return StreamingResponse(chunks(), media_type="text/plain; charset=utf-8")


@app.post("/extract")
async def extract(body: ChatIn) -> Person:
    """成功返回 Person（HTTP 200 + JSON）；模型胡言则 422。

    返回类型写成 Person，FastAPI 会用 pydantic 把对象转成 JSON。对照 @RestController 返回 DTO。
    """
    client = _client()
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[
                {"role": "system", "content": "只返回 JSON。"},
                {"role": "user", "content": body.text},
            ],
            response_format={"type": "json_object"},  # 请模型（假模型会照做）吐 JSON 对象。
            temperature=0,
        )
        raw = resp.choices[0].message.content or ""
        try:
            # 解析并校验。成功就 return，FastAPI 负责把它写成响应 JSON。
            return Person.model_validate_json(raw)
        except ValidationError:
            # 模型返回了脏 JSON 或字段不合法。把它变成 HTTP 422，而不是让连接 500。
            # raise HTTPException 是抛异常，不是 return。FastAPI 的异常处理器会接住并写成响应。
            # 对照：throw new ResponseStatusException(422, "...")。
            raise HTTPException(status_code=422, detail="模型没有返回合法 JSON")
    finally:
        await client.close()


def main() -> None:
    """起假模型 → TestClient 打两个接口 → 退出。不必手动 uvicorn。"""
    server, base_url = start_mock()  # 后台线程听一个随机端口。
    # 写进环境变量，上面的 _client() 才能读到这次的地址。这是改本进程的环境，不是改系统。
    os.environ["OPENAI_BASE_URL"] = base_url
    # setdefault：只有还没有这个键时才设。已经 export 过真密钥的话，不会被覆盖成 mock-key。
    os.environ.setdefault("OPENAI_API_KEY", "mock-key")
    try:
        # TestClient(app)：不 listen 端口，用 WSGI/ASGI 直接调 app。对照 MockMvcBuilders.standaloneSetup(app)。
        client = TestClient(app)
        # json= 会设 Content-Type 并序列化成请求体。对照 mockMvc.perform(post("/chat").contentType(JSON).content(...))。
        streamed = client.post("/chat", json={"text": "你好, hudi"})
        # 流式在 TestClient 里会被收齐，streamed.text 是拼完的整段。status_code 对照 response.getStatus()。
        print("GET 不是这个接口；POST /chat =", streamed.status_code, streamed.text)

        ok = client.post("/extract", json={"text": "抽取"})
        # ok.json() 把响应体解析成 dict。合法时假模型回 hudi / 70，状态码 200。
        print("POST /extract 合法 =", ok.status_code, ok.json())

        bad = client.post("/extract", json={"text": "TRIGGER:BADJSON"})
        # 路由里 raise 了 HTTPException(422)。这里只打印状态码，不调用 .json() 也行。
        print("POST /extract 脏 JSON =", bad.status_code)
    finally:
        server.shutdown()  # TestClient 用完就停假模型。


if __name__ == "__main__":
    # TestClient 内部会跑事件循环；不要再 asyncio.run 包一层，否则会和它抢循环。
    main()
    # 若想看 /docs：先 start_mock 并 export OPENAI_BASE_URL，再
    #   cd 31-FastAPI流式接口
    #   python -m uvicorn 31_app:app --port 8000
    # 目录名带连字符，uvicorn 的 31_app:app 必须在本目录执行，不能从仓库根写「31-FastAPI流式接口.31_app:app」。
