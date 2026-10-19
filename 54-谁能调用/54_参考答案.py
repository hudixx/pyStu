"""第 54 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
无令牌 401
有效 200 {'user': 'hudi'}
改过 401

没有令牌是 401。用演示密钥签发给 hudi，带头访问是 200，用户是 hudi。
改掉一个字符再访问，是 401。签名用 compare_digest 比较，没有把真的长密钥写进文件。

练习里有两处写错，这次没暴露，是因为签发和校验用的是同一个函数：
- separators 写成了 (" ,", ":")，项和项之间是「空格加逗号」。
  头会变成 {"alg":"HS256" ,"typ":"JWT"}。应写成 (",", ":")，不要空格。
  自己签的令牌还能对上。换成按正常 JSON 签的令牌，签名会对不上。
- 填充写成了 -len(text) & 4。& 是按位与，结果只有 0 或 4。
  hudi 这一段正确的填充是 1 个 =。这次多补了 4 个，Python 仍解出了用户名，所以题 2 过了。
  应写成 -len(text) % 4。% 得到 0、1、2 或 3，正好补到 4 的倍数。
- 签名做成了 base64。教程用十六进制，是为了能读。两种都能让「改一个字」变成 401。
  生产用 PyJWT，不要抄这段。默认值 dev_secret 和教程的 dev-secret 不是同一串，
  只要签发和校验用同一个就行。它不是真密钥，不要换成真的再提交。

题 3：
- 之后的请求带令牌，不把密码放进每个请求。
  密码只用来换令牌。之后每个请求带令牌。密码出现的次数少，
  日志、代理里不会每个请求都留下密码。
  令牌可以过期、可以作废，不必因此改密码。本课没有作废列表，知道有这件事即可。
  令牌泄漏了要作废，不是把密码再传一遍。
- 改了 payload 之后，不能自己把签名换成同样长的另一串就通过。
  签名不是「长度对就行」。服务端用 APP_SECRET 对前两段重新算 HMAC，再和第三段比。
  你没有密钥，算不出那一串。自己换成同样长的另一串，compare_digest 对不上，就是 401。
  头和载荷只是编码，谁都能解开。防改靠第三段，而第三段离开密钥算不出来。
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
    """JSON 再做 url 安全的 base64，去掉末尾的 =。"""

    # separators 去掉空格。同一份数据必须签出同一串。
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> dict:
    """补回 base64 需要的填充，再解成 dict。"""

    # 长度已经是 4 的倍数时得到 0。否则补 1 到 3 个等号。用 %，不要用 &。
    padding = "=" * (-len(text) % 4)
    raw = base64.urlsafe_b64decode(text + padding)
    return json.loads(raw.decode())


def sign(sub: str, secret: str) -> str:
    """签发。头和载荷只是编码。防改靠第三段。"""

    header = _b64({"alg": "HS256", "typ": "JWT"})
    payload = _b64({"sub": sub})
    signing = f"{header}.{payload}"
    # 十六进制是为了能读。生产 JWT 的签名是 base64，并且应使用 PyJWT。
    signature = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    return f"{signing}.{signature}"


def verify(token: str, secret: str) -> str:
    """先重算签名，再解载荷。不要先相信载荷里的用户名。"""

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("令牌不是三段")
    header, payload, signature = parts
    signing = f"{header}.{payload}"
    expected = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    # compare_digest 比签名，避免普通 == 在第一个不同字符就返回。
    if not hmac.compare_digest(expected, signature):
        raise ValueError("签名不符")
    body = _unb64(payload)
    sub = body.get("sub")
    if not isinstance(sub, str) or sub == "":
        raise ValueError("没有 sub")
    return sub


def current_user(authorization: str | None = Header(default=None)) -> str:
    """没有、不是 Bearer、签名不对，都是 401。内部原因不写进响应。"""

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少令牌")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify(token, _SECRET)
    except ValueError:
        raise HTTPException(status_code=401, detail="令牌无效") from None


@app.get("/me")
def me(user: str = Depends(current_user)) -> dict:
    """校验通过才进这里。用户名来自令牌，不来自查询参数。"""

    return {"user": user}


def main() -> None:
    client = TestClient(app)
    missing = client.get("/me")
    print("无令牌", missing.status_code)

    token = sign("hudi", _SECRET)
    ok = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    print("有效", ok.status_code, ok.json())

    # 改一个字符。第二个字符如果已经是 A，就改成 B，保证和原来不同。
    tampered = token[0] + ("A" if token[1] != "A" else "B") + token[2:]
    bad = client.get("/me", headers={"Authorization": f"Bearer {tampered}"})
    print("改过", bad.status_code)


if __name__ == "__main__":
    main()
