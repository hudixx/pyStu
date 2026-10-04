# 第 31 课：从 Controller 看流式问答接口

阶段六收口：把 26–30 装进 FastAPI。结束标准是：

- 流式返回
- 非法 JSON 能失败
- 超时写得出来（客户端 timeout）

运行示例有两种。

**A. 当脚本跑（推荐先看这个，不占端口）：**

```bash
PYTHONUTF8=1 python 31-FastAPI流式接口/31_app.py
```

它会起假模型，用 `TestClient` 打自己的 `/chat` 和 `/extract`，打完退出。

**B. 真听端口（看 `/docs`）：**

```bash
cd 31-FastAPI流式接口
PYTHONUTF8=1 python -c "import uvicorn; from importlib.util import spec_from_loader"
```

更省事：在 `31_app.py` 里已经留了注释。需要时：

```bash
cd 31-FastAPI流式接口
# 先另开终端跑假模型不方便，脚本模式足够交作业
```

本课作业按 **A** 交一份能被 TestClient 打的 `31_练习.py` 即可，不必 uvicorn 挂着。

---

## 1. 流式接口

```python
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    async def chunks():
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
    return StreamingResponse(chunks(), media_type="text/plain; charset=utf-8")
```

对照：Spring 的 `Flux<String>` / SSE。这里吐纯文本，前端按块拼。不要在 `async def` 里用同步 `OpenAI()`。

`client` 在模块级建一次（连接池），`timeout=` 必写。应用生命周期里 `await client.close()` 第 10 阶段再补，本课脚本结束进程即可。

---

## 2. JSON 接口：失败就是 4xx/5xx

```python
@app.post("/extract")
async def extract(body: ChatIn) -> Person:
    resp = await client.chat.completions.create(
        ...,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or ""
    try:
        return Person.model_validate_json(raw)
    except ValidationError:
        raise HTTPException(status_code=422, detail="模型没有返回合法 JSON")
```

`TRIGGER:BADJSON` 必须 422，不能 200 一个空对象。

---

## 3. 密钥仍走环境变量

模块里：

```python
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
    base_url=os.environ.get("OPENAI_BASE_URL"),  # 脚本里会先 start_mock 再改这个
    timeout=10.0,
    max_retries=0,
)
```

示例会在 `main` 里先 `start_mock()`，再 `os.environ["OPENAI_BASE_URL"] = base_url`，再 import / 重建 client。注意：**AsyncOpenAI 创建时读 base_url**，要在造 client 之前设好环境变量，或直接把 `base_url` 传进构造器。

---

## 本课肌肉记忆

1. 流式用 `StreamingResponse` + `async for`
2. JSON 用 pydantic，脏数据 422
3. timeout 写在 SDK 客户端上
4. 密钥不进源码
5. 还没有 RAG、没有 Agent。能把模型当可靠 HTTP 用，阶段六就够了

阶段七才是检索。说「开始阶段七」再写教程。
