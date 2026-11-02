"""验收第 4 课：接口要令牌，日志不带密钥，测试里的模型是假的。

dev-secret 只给这门课的本地断言。不是生产密钥，不要换成真的。
问题里的 sk-demo1234 也是课里的假样例，用来证明日志会换掉它。
"""

from __future__ import annotations

import hmac

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from types import SimpleNamespace


class FakeClient:
    """chat.completions.create 的形状。不访问网络。"""

    def __init__(self) -> None:
        self.calls = 0
        self.chat = self  # client.chat.completions.create 三个点都落在这一个对象上。
        self.completions = self

    async def create(self, **_kwargs: object) -> SimpleNamespace:
        """假的补全。内容固定，并留下 usage，好让调用方能读 token。"""

        self.calls += 1
        message = SimpleNamespace(content="回声")
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        return SimpleNamespace(choices=[choice], usage=usage)


def allowed(header: str | None, secret: str) -> bool:
    """Bearer 后面的令牌和约定的一样才通过。缺头、格式不对，都是否。"""

    if header is None or not header.startswith("Bearer "):
        return False
    got = header.removeprefix("Bearer ")
    # compare_digest 按字节比，避免用 == 提前返回。两边都要是 bytes。
    return hmac.compare_digest(got.encode(), secret.encode())


def redact(text: str) -> str:
    """日志里不留这个假密钥。只替换这一串，不猜别的秘密长什么样。"""

    return text.replace("sk-demo1234", "***")


def build_app(client: FakeClient, secret: str = "dev-secret") -> FastAPI:
    """每个测试造自己的 app 和自己的假客户端。calls 不串到下一则。"""

    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}  # 健康检查不需要令牌。

    @app.post("/ask")
    async def ask(request: Request) -> JSONResponse:
        if not allowed(request.headers.get("authorization"), secret):
            return JSONResponse({"detail": "未授权"}, status_code=401)
        body = await request.json()
        question = str(body.get("question") or "")
        # 先打日志，再决定叫不叫模型。地址题也不该把密钥打出去。
        print("问句", redact(question))
        if "地址" in question:
            return JSONResponse({"answer": "不知道"})
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": question}],
        )
        return JSONResponse(
            {
                "answer": resp.choices[0].message.content,
                "prompt_tokens": resp.usage.prompt_tokens,
            }
        )

    return app


def _client(fake: FakeClient) -> TestClient:
    return TestClient(build_app(fake))


def test_health() -> None:
    response = _client(FakeClient()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_no_token() -> None:
    response = _client(FakeClient()).post("/ask", json={"question": "你好"})
    assert response.status_code == 401


def test_echo() -> None:
    fake = FakeClient()
    response = _client(fake).post(
        "/ask",
        json={"question": "你好"},
        headers={"Authorization": "Bearer dev-secret"},
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "回声"
    assert response.json()["prompt_tokens"] == 1
    assert fake.calls == 1


def test_address_skips_model() -> None:
    fake = FakeClient()
    response = _client(fake).post(
        "/ask",
        json={"question": "公司地址在哪"},
        headers={"Authorization": "Bearer dev-secret"},
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "不知道"
    assert fake.calls == 0


def test_log_hides_secret(capsys) -> None:
    response = _client(FakeClient()).post(
        "/ask",
        json={"question": "我的密钥是 sk-demo1234"},
        headers={"Authorization": "Bearer dev-secret"},
    )
    assert response.status_code == 200
    captured = capsys.readouterr()
    assert "sk-demo1234" not in captured.out
    assert "***" in captured.out
