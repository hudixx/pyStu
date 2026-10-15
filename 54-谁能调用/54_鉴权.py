"""第 54 课示例：没有令牌不能调用。令牌被改过也不能调用。

这是三段的签名令牌，用来看懂 header.payload.signature。
签名用十六进制，是为了能读。生产用 PyJWT 这一类库，不要把这段抄进正式服务。
密钥来自环境变量。这里的默认值只给本课演示，不是真的密钥。
"""

from __future__ import annotations

import base64  # urlsafe 的 base64。JWT 的头和载荷是这种编码，不是加密。
import hashlib  # sha256。对照 MessageDigest.getInstance("SHA-256")。
import hmac  # 带密钥的哈希。对照 Mac.getInstance("HmacSHA256")。没有密钥，任何人都能改载荷再重签。
import json  # 头和载荷都是紧凑的 JSON。对照自己写 ObjectMapper，这里用标准库。
import os  # 读 APP_SECRET。对照 System.getenv。

# Header 从请求头里取值。HTTPException 变成对应状态码。对照从 HttpServletRequest 拿 header，失败抛 401。
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

# 演示用的默认值。生产必须改掉，并且不要写进仓库。
# 模块加载时读一次。对照 static final，但进程启动之后再改环境变量，这个名字不会跟着变。
_SECRET = os.environ.get("APP_SECRET", "dev-secret")
app = FastAPI(title="第 54 课")


def _b64(data: dict) -> str:
    """JSON 再做 url 安全的 base64，去掉末尾的 =。对照 JWT 的一段。"""
    # separators 去掉空格。默认 dumps 会在逗号和冒号后加空格，同一份数据会签出不同的字符串。
    # encode() 不带参数，按 utf-8 把 str 变成 bytes。base64 吃的是字节。
    raw = json.dumps(data, separators=(",", ":")).encode()
    # urlsafe：用 - 和 _，避免 + / 在 URL 或请求头里被误读。decode() 把 bytes 变回 str。
    # rstrip("=") 去掉尾部填充。JWT 习惯不带这些等号，验的时候再补回去。
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> dict:
    """补回 base64 需要的填充，再解成 dict。"""
    # base64 要求长度是 4 的倍数。去掉的等号个数就是「差多少到下一个倍数」。
    # -len(text) % 4：长度已经是 4 的倍数时得到 0，不补；差 1 个补 1 个，差 2 个补 2 个。
    padding = "=" * (-len(text) % 4)
    raw = base64.urlsafe_b64decode(text + padding)  # 得到当初 dumps 出来的那些字节。
    return json.loads(raw.decode())  # decode 默认 utf-8。loads 把 JSON 文本变回 dict。


def sign(sub: str, secret: str) -> str:
    """签发。sub 是用户名。三段用点连起来。

    头和载荷只是编码，谁都能解开。防改靠第三段：用密钥对前两段做 HMAC。
    """
    header = _b64({"alg": "HS256", "typ": "JWT"})  # alg 声明用的算法。本课只认这一种，没有真的去读它再分支。
    payload = _b64({"sub": sub})  # 载荷。本课只有用户名，没有过期时间。生产的令牌必须有 exp。
    signing = f"{header}.{payload}"  # 被签名的原文就是这两段，中间一个点。第三段不参与「被签的内容」。
    # hmac.new(密钥字节, 消息字节, 算法)。hexdigest 得到十六进制字符串，所以你能在打印里读到它。
    # 生产 JWT 的签名是 base64，不是十六进制。不要把这一行抄进正式服务。
    signature = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    return f"{signing}.{signature}"


def verify(token: str, secret: str) -> str:
    """校验签名，返回 sub。结构不对或签名不对，都抛 ValueError。

    先重算签名，再解载荷。不要先相信载荷里的用户名。
    """
    parts = token.split(".")  # 不限次数。多于或少于两刀，段数就不是 3。
    if len(parts) != 3:
        raise ValueError("令牌不是三段")
    # 三个名字一次接住。对照拆一个数组，先检查 length 再按下标取，避免 IndexError。
    header, payload, signature = parts
    signing = f"{header}.{payload}"  # 用令牌里的前两段重算。不用客户端另外传来的「原文」。
    expected = hmac.new(secret.encode(), signing.encode(), hashlib.sha256).hexdigest()
    # compare_digest 用来比签名，避免普通 != 在时间上露出差异。对照 MessageDigest.isEqual。
    # 普通 == 在发现第一个不同字符时就返回，比较时间能被用来猜签名。这个函数每次比较的耗时更接近。
    if not hmac.compare_digest(expected, signature):
        raise ValueError("签名不符")
    body = _unb64(payload)  # 签名对上了才解码。这里解出来的仍是客户端当初写的内容，只是没被改过。
    sub = body.get("sub")  # 没有这个键得到 None，不抛 KeyError。
    # isinstance 对照 instanceof。数字 1、空串、None 都不是合法用户名。
    if not isinstance(sub, str) or sub == "":
        raise ValueError("没有 sub")
    return sub


def current_user(authorization: str | None = Header(default=None)) -> str:
    """从 Authorization 头取出令牌。没有、不是 Bearer、签名不对，都是 401。

    Header(default=None) 是标记，不是「现在就去读请求」。FastAPI 每次请求才填充。
    str | None 对照 @Nullable String。没传这个头时是 None，不是空串。
    """
    # startswith 对照 startsWith。大小写按字面比较，"bearer " 不会通过。本课要求标准的 "Bearer "。
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少令牌")
    # removeprefix 只去掉开头这一次。对照 substring("Bearer ".length())，但名字写清楚了在去掉什么。
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify(token, _SECRET)  # 返回的字符串会成为路由参数 user。对照过滤器把用户放进请求属性。
    except ValueError:
        # 结构坏了、签名不符、没有 sub，对客户端都是同一句，不把内部原因写进响应。
        # from None：不要把 ValueError 当成这个 401 的「原因」附在栈上。对照抛新异常时不把内部异常回给调用方。
        raise HTTPException(status_code=401, detail="令牌无效") from None


@app.get("/me")
def me(user: str = Depends(current_user)) -> dict:
    """只有校验通过才进这里。返回的是令牌里的 sub，不是客户端自己说的名字。

    Depends(current_user)：先跑上面的函数。它抛 401，这个函数不会执行。对照拦截器没放行就不进 Controller。
    """
    return {"user": user}


def main() -> None:
    client = TestClient(app)  # 不占端口。对照 MockMvc。
    missing = client.get("/me")  # 不带 Authorization。
    print("无令牌", missing.status_code)  # 预期 401。

    token = sign("hudi", _SECRET)  # 用和校验相同的密钥签发。密钥不一致，签名一定对不上。
    ok = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    print("有效", ok.status_code, ok.json())  # 预期 200，user 是 hudi。

    # 改 payload 的一个字符。签名是对原文算的，对不上。
    # token[0] 是第一个字符，token[1] 是第二个，token[2:] 是从第三个到末尾。切片含起点、不含终点。
    # 第二个字符如果已经是 A，就改成 B，否则改成 A。这样一定和原来不同，不会「碰巧改成原字符」。
    tampered = token[0] + ("A" if token[1] != "A" else "B") + token[2:]
    bad = client.get("/me", headers={"Authorization": f"Bearer {tampered}"})
    print("改过", bad.status_code)  # 预期 401。改的是头或载荷的一个字符，第三段没跟着重算。


if __name__ == "__main__":
    main()
