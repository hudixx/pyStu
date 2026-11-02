"""验收第 4 课：接口要令牌，日志不带密钥，测试里的模型是假的。

dev-secret 只给这门课的本地断言。不是生产密钥，不要换成真的。
问题里的 sk-demo1234 也是课里的假样例，用来证明日志会换掉它。

本文件没有 main。pytest 会自己找出名字以 test_ 开头的函数来跑。直接 python 本文件不会跑这些测试。
"""

from __future__ import annotations

import hmac  # 带密钥的比较。这里只用 compare_digest，按固定时间比两段字节。对照 MessageDigest.isEqual。

from fastapi import FastAPI, Request  # Request 是原始请求。本课要自己读 header 和 JSON，所以不用 pydantic 模型当参数。
from fastapi.responses import JSONResponse  # 指定状态码和 JSON 正文。对照 ResponseEntity。
from fastapi.testclient import TestClient  # 进程内客户端，不占端口。对照 MockMvc。
from types import SimpleNamespace  # 一个只有属性的空对象。用来假装 SDK 返回值上的 .content、.usage。


class FakeClient:
    """chat.completions.create 的形状。不访问网络。

    业务代码写 client.chat.completions.create(...)。这里没有真正的三层对象，三个名字都指回自己。
    对照一个 mock 的链式调用都返回自己。Java 必须先有接口，Python 只要点出来的路径在。
    """

    def __init__(self) -> None:
        """每个假客户端自己的调用次数从 0 开始。测试用它断言「打没打到模型」。"""

        self.calls = 0
        self.chat = self  # client.chat.completions.create 三个点都落在这一个对象上。
        self.completions = self

    async def create(self, **_kwargs: object) -> SimpleNamespace:
        """假的补全。内容固定，并留下 usage，好让调用方能读 token。

        逻辑：calls 加 1，然后搭出 choices[0].message.content 和 usage.prompt_tokens 这两条路径。
        **_kwargs 把 model、messages 这些关键字参数收成字典，然后故意不用。下划线表示「参数我收下但不读」。
        对照方法接受 Map，测试不关心里面的提示词。async 是因为路由里写了 await。
        """

        self.calls += 1
        message = SimpleNamespace(content="回声")  # 造出 .content。对照一个 public 字段，不是真的 SDK 类型。
        choice = SimpleNamespace(message=message)  # 再点一层 .message。
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        # choices 是列表，调用方取 [0]。下标从 0 开始。
        return SimpleNamespace(choices=[choice], usage=usage)


def allowed(header: str | None, secret: str) -> bool:
    """Bearer 后面的令牌和约定的一样才通过。缺头、格式不对，都是否。

    逻辑：
    1. header 是 None，或者不是以 "Bearer " 开头，返回 False。
    2. 去掉这个前缀，剩下的和 secret 都编成字节，用 compare_digest 比。
    一样才是 True。比的是内容，但不用 ==，避免比较时间露出差异。
    str | None 对照这个参数可以是字符串，也可以是 None。没传 Authorization 时，下面拿到的是 None。
    """

    if header is None or not header.startswith("Bearer "):
        # is None 只认空。startswith 对照 startsWith，大小写按字面比，"bearer " 不会通过。
        # or 短路：左边已经是真，右边不再调用 startswith，所以 None 不会在这里抛错。
        return False
    got = header.removeprefix("Bearer ")  # 只去掉开头这一次。对照 substring("Bearer ".length())。
    # compare_digest 按字节比，避免用 == 提前返回。两边都要是 bytes。
    # encode() 不写参数就是 UTF-8。对照 getBytes(UTF_8)。
    # == 发现第一个不同字符就返回，比较花的时间能被用来猜令牌。compare_digest 每次的耗时更接近。
    return hmac.compare_digest(got.encode(), secret.encode())


def redact(text: str) -> str:
    """日志里不留这个假密钥。只替换这一串，不猜别的秘密长什么样。

    逻辑：把 sk-demo1234 换成 ***。原文里没有这串，就原样返回。str 不可变，replace 给出一个新字符串。
    """

    return text.replace("sk-demo1234", "***")  # 替换所有出现。对照 replace，得到的是新字符串。


def build_app(client: FakeClient, secret: str = "dev-secret") -> FastAPI:
    """每个测试造自己的 app 和自己的假客户端。calls 不串到下一则。

    逻辑：造一个 FastAPI，挂上 /health 和 /ask。
    /health 不看令牌，固定返回 ok。
    /ask 先验 Authorization。不对就 401。对了再读 JSON。
    问句先脱敏再打印。含「地址」就回答不知道，不调用模型。其他问句才 await 假的 create。
    secret 的 = "dev-secret" 是默认值。调用时不传，就用这一串。这是课里的假令牌。
    """

    app = FastAPI()  # 空应用。路由靠下面的装饰器登记上去。对照一个还没有 Controller 的上下文。

    @app.get("/health")
    async def health() -> dict[str, str]:
        """健康检查。不读令牌，不碰模型。返回的字典会被 FastAPI 收成 JSON。"""

        return {"status": "ok"}  # 健康检查不需要令牌。

    @app.post("/ask")
    async def ask(request: Request) -> JSONResponse:
        """问答。先鉴权，再脱敏打日志，地址题不调用模型。

        逻辑：
        1. 从请求头取 authorization。没有这个头，get 得到 None。
        2. allowed 不过就返回 401，函数在这里结束，不会读正文，也不会调用模型。
        3. await request.json() 把正文解析成字典。question 缺了或是空，收成空串。
        4. 打印脱敏后的问句。然后含「地址」就直接返回「不知道」。
        5. 其他问句才调用假模型，把回答和 prompt_tokens 放进 200 的 JSON。
        """

        if not allowed(request.headers.get("authorization"), secret):
            # headers.get 对照取请求头，没有就 None，不抛。HTTP 头名在这里按小写取。
            # secret 是外层 build_app 的参数。嵌套函数能看见它。对照匿名类抓住外面的局部变量。
            return JSONResponse({"detail": "未授权"}, status_code=401)
        body = await request.json()  # 异步读 JSON。结果是 dict。对照自己读输入流再解析。
        question = str(body.get("question") or "")
        # get 没有这个键时返回 None。or "" 把 None 和空串都收成 ""。再 str() 兜住不是字符串的值。
        # 先打日志，再决定叫不叫模型。地址题也不该把密钥打出去。
        print("问句", redact(question))
        if "地址" in question:
            # in 是子串。含「地址」就不调用模型。对照 question.contains("地址")。
            return JSONResponse({"answer": "不知道"})  # 不写 status_code 就是 200。
        resp = await client.chat.completions.create(
            model="mock-chat",  # 假的 create 用 **_kwargs 接住，不会因为多了这些参数而报错。
            messages=[{"role": "user", "content": question}],
        )
        return JSONResponse(
            {
                "answer": resp.choices[0].message.content,  # 假对象上搭好的「回声」。
                "prompt_tokens": resp.usage.prompt_tokens,  # 假 usage 里写死的 1。
            }
        )

    return app  # 两个路由都登记完，把应用交回测试。对照把配好的上下文交出去。


def _client(fake: FakeClient) -> TestClient:
    """用这个假客户端包一层进程内测试客户端。下划线开头表示给本文件自己用。

    逻辑：build_app 不传 secret，于是用默认的 dev-secret。TestClient 不监听端口。
    """

    return TestClient(build_app(fake))


def test_health() -> None:
    """没有令牌也能访问健康检查。状态码 200，正文是 status=ok。

    断言失败会抛 AssertionError，pytest 把这个测试标成失败。== 对字典是比键和值，不是比是不是同一个对象。
    """

    response = _client(FakeClient()).get("/health")  # 这一则自己的假客户端。健康检查不会让 calls 增加。
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}  # json() 把响应体解析成 dict。对照读响应再比对字段。


def test_no_token() -> None:
    """问句合法，但没有 Authorization，应是 401。不看回答正文。"""

    response = _client(FakeClient()).post("/ask", json={"question": "你好"})
    # json= 会序列化成请求体并带上 Content-Type。这里故意不传 headers。
    assert response.status_code == 401


def test_echo() -> None:
    """令牌正确、问句不是地址，应打到假模型一次。回答是「回声」，prompt_tokens 是 1。"""

    fake = FakeClient()  # 先留住这个对象，后面才能读 fake.calls。写在调用里就拿不回来了。
    response = _client(fake).post(
        "/ask",
        json={"question": "你好"},
        headers={"Authorization": "Bearer dev-secret"},  # 和默认 secret 相同，allowed 才为真。
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "回声"  # 方括号取字典的键。没有这个键会抛 KeyError。
    assert response.json()["prompt_tokens"] == 1
    assert fake.calls == 1


def test_address_skips_model() -> None:
    """问公司地址。仍要令牌，但 calls 必须仍是 0。回答是「不知道」。"""

    fake = FakeClient()
    response = _client(fake).post(
        "/ask",
        json={"question": "公司地址在哪"},
        headers={"Authorization": "Bearer dev-secret"},
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "不知道"
    assert fake.calls == 0  # 含「地址」的分支在 create 之前就 return 了。


def test_log_hides_secret(capsys) -> None:
    """问句里夹着假密钥。响应仍是 200，但 pytest 抓住的标准输出里不能再有这串原文。

    capsys 是 pytest 自己的夹具，按参数名注入。它把 print 接走，测试结束后用 readouterr 取回来。
    不需要从本文件 import。参数名必须叫 capsys，改了就接不上。
    """

    response = _client(FakeClient()).post(
        "/ask",
        json={"question": "我的密钥是 sk-demo1234"},
        headers={"Authorization": "Bearer dev-secret"},
    )
    assert response.status_code == 200
    captured = capsys.readouterr()  # 取出到目前为止的 stdout 和 stderr。print 在 out 里。
    assert "sk-demo1234" not in captured.out  # not in 是「不是子串」。原文还在就失败。
    assert "***" in captured.out  # 占位必须在。只断言「原文不在」还不够，可能根本没打印。

# 这个脚本想说明的事：
# /health 不要令牌。/ask 没有 Bearer，或令牌和约定的不一样，就是 401。
# 令牌用 compare_digest 比字节，不用 ==。问句进日志之前先把 sk-demo1234 换成 ***。
# 测试里的模型是假的。含「地址」不调用它，calls 仍是 0。其他问句才打一次，回答固定是「回声」。
