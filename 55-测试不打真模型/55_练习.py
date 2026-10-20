from __future__ import annotations
from types import SimpleNamespace

class FakeClient:
    def __init__(self) -> None:
        self.calls = 0
        self.chat = self
        self.completions = self

    async def create(self, **kwargs) -> SimpleNamespace:
        self.calls += 1
        message = SimpleNamespace(content="回声")
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        return SimpleNamespace(choices=[choice], usage=usage)


async def answer(client: FakeClient, question: str) -> str:
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

