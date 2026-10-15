"""第 54 课示例：没有令牌不能调用。令牌被改过也不能调用。

这是三段的签名令牌，用来看懂 header.payload.signature。
签名用十六进制，是为了能读。生产用 PyJWT 这一类库，不要把这段抄进正式服务。
密钥来自环境变量。这里的默认值只给本课演示，不是真的密钥。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

# 演示用的默认值。生产必须改掉，并且不要写进仓库。
_SECRET = os.environ.get("APP_SECRET", "dev-secret")
app = FastAPI(title="第 54 课")


def _b64(data: dict) -> str:
    """JSON 再做 url 安全的 base64，去掉末尾的 =。对照 JWT 的一段。"""
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> dict:
    """补回 base64 需要的填充，再解成 dict。"""
    padding = "=" * (-len(text) % 4)
    raw = base64.urlsafe_b64decode(text + padding)
    return json.loads(raw.decode())


def sign(sub: str, secret: str) -> str:
    """签发。sub 是用户名。三段用点连起来。"""
    header = _b64({"alg": "HS256", "typ": "JWT"})
    payload = _b64({"sub": sub})
    signing = f"{header}.{payload}"
    signature = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    return f"{signing}.{signature}"


def verify(token: str, secret: str) -> str:
    """校验签名，返回 sub。结构不对或签名不对，都抛 ValueError。"""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("令牌不是三段")
    header, payload, signature = parts
    signing = f"{header}.{payload}"
    expected = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    # compare_digest 用来比签名，避免普通 != 在时间上露出差异。对照 MessageDigest.isEqual。
    if not hmac.compare_digest(expected, signature):
        raise ValueError("签名不符")
    body = _unb64(payload)
    sub = body.get("sub")
    if not isinstance(sub, str) or sub == "":
        raise ValueError("没有 sub")
    return sub


def current_user(authorization: str | None = Header(default=None)) -> str:
    """从 Authorization 头取出令牌。没有、不是 Bearer、签名不对，都是 401。"""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少令牌")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify(token, _SECRET)
    except ValueError:
        raise HTTPException(status_code=401, detail="令牌无效") from None


@app.get("/me")
def me(user: str = Depends(current_user)) -> dict:
    """只有校验通过才进这里。返回的是令牌里的 sub，不是客户端自己说的名字。"""
    return {"user": user}


def main() -> None:
    client = TestClient(app)
    missing = client.get("/me")
    print("无令牌", missing.status_code)

    token = sign("hudi", _SECRET)
    ok = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    print("有效", ok.status_code, ok.json())

    # 改 payload 的一个字符。签名是对原文算的，对不上。
    tampered = token[0] + ("A" if token[1] != "A" else "B") + token[2:]
    bad = client.get("/me", headers={"Authorization": f"Bearer {tampered}"})
    print("改过", bad.status_code)


if __name__ == "__main__":
    main()
