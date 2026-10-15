"""第 55 课示例：测试里的模型是假的。地址题不调用它。

对照 Mockito。CI 里不要打付费接口，也不要指望网络。
这里不用 pytest 启动器。断言写在脚本里，python 直接跑。pytest 只是把这些断言收进测试方法。
"""

from __future__ import annotations

from types import SimpleNamespace


class FakeClient:
    """形状上有 chat.completions.create，这样业务代码不用为测试改写法。"""

    def __init__(self) -> None:
        self.calls = 0
        self.chat = self  # client.chat.completions.create 会走到下面的 create。
        self.completions = self

    async def create(self, **kwargs) -> SimpleNamespace:
        self.calls += 1
        # 测试不关心文采。固定一句，并留下 usage，好让调用方能读 token。
        message = SimpleNamespace(content="回声")
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        return SimpleNamespace(choices=[choice], usage=usage)


async def answer(client: FakeClient, question: str) -> str:
    """地址题直接拒答，不碰 client。其他问题才调用模型。"""
    if "地址" in question:
        return "不知道"
    resp = await client.chat.completions.create(
        model="mock-chat",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content


async def main_async() -> None:
    client = FakeClient()
    address = await answer(client, "公司地址在哪")
    # 拒答之后，调用次数必须仍是 0。这是这课要守住的断言。
    assert address == "不知道"
    assert client.calls == 0

    text = await answer(client, "你好")
    assert text == "回声"
    assert client.calls == 1
    print("地址", address, "调用", 0)
    print("你好", text, "调用", client.calls)


def main() -> None:
    import asyncio

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
