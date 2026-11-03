from __future__ import annotations

import hmac
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0
        self.chat = self
        self.completions = self

    async def create(self, **_kwargs: object) -> SimpleNamespace:
        self.calls += 1
        message = SimpleNamespace(content="回声")
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        return SimpleNamespace(choices=[choice], usage=usage)


def allowed(header: str | None, secret: str) -> bool:
    if header is None or not header.startswith("Bearer "):
        return False
    got = header.removeprefix("Bearer ")
    return hmac.compare_digest(got.encode(), secret.encode())


def redact(text: str) -> str:
    return text.replace("sk-demo1234", "***")


def build_app(client: FakeClient, secret: str = "dev-secret") -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/ask")
    async def ask(request: Request) -> JSONResponse:
        if not allowed(request.headers.get("authorization"), secret):
            return JSONResponse({"detail": "未授权"}, status_code=401)
        body = await request.json()
        question = str(body.get("question") or "")
        print("问句", redact(question))
        if "工资" in question:
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


def test_pay_skips_model() -> None:
    fake = FakeClient()
    response = _client(fake).post(
        "/ask",
        json={"question": "工资多少"},
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
