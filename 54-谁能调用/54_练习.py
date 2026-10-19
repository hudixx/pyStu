from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

_SECRET =  os.environ.get('APP_SECRET', "dev_secret")
app = FastAPI(title="54练习")

def _b64(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")
def _unb64(text: str) -> dict:
    padding = "=" * (-len(text) % 4)
    raw = base64.urlsafe_b64decode(text + padding)
    return json.loads(raw.decode())

def sign (sub: str, secret: str) -> str:
    header = _b64({"alg": "HS256", "typ": "JWT"})
    payload = _b64({"sub": sub})
    signing = f"{header}.{payload}"
    signature = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).digest()
    signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{signing}.{signature}"

def  verify(token: str, secret: str) -> str:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("令牌不是三段")
    header, payload, signature = parts
    signing = f"{header}.{payload}"
    expected = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).digest()
    expected = base64.urlsafe_b64encode(expected).decode().rstrip("=")
    if not hmac.compare_digest(expected,signature):
        raise ValueError("签名不符")
    body = _unb64(payload)
    sub = body.get("sub")
    if not isinstance(sub, str) or sub == "":
        raise ValueError("没有 sub")
    return sub

def current_user(authorization: str | None = Header(default=None)) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少令牌")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify(token, _SECRET)
    except ValueError:
        raise HTTPException(status_code=401, detail="令牌无效") from None


@app.get("/me")
def me(user: str = Depends(current_user)) -> dict:
    return {"user": user}

def main() -> None:
    client = TestClient(app)
    missing = client.get("/me") # 不带认证
    print("无令牌", missing.status_code)
    token = sign("hudi", _SECRET)
    ok = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    print("有效", ok.status_code, ok.json())  # 预期 200，user 是 hudi。
    tampered = token[0] + ("A" if token[1] != "A" else "B" ) + token[2:]
    bad = client.get("/me", headers={"Authorization": f"Bearer {tampered}"})
    print("改过", bad.status_code)


if __name__ == "__main__":
    main()

# 题3不知道，请在参考答案的注释中个给出