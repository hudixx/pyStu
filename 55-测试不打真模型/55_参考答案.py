"""第 55 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
地址 不知道 调用 0
你好 回声 调用 1

公司地址在哪 得到「不知道」，assert 卡住调用次数是 0。
你好 得到「回声」，调用次数变成 1。
没有 import openai，也没有 start_mock。假客户端自己数 calls。

题 3 这次文件里没有写。答案如下。

题 3：
- 这课不允许把第 26 课的假 HTTP 服务叫起来。
  start_mock 是本机起一个 HTTP 服务。业务代码仍要 import openai，仍要发 HTTP。
  CI 就要占端口、等服务起来，还可能连到真的网关。
  这课要证明的是：不该打的时候一次都没打，该打的时候打的是你注入的对象。
  断言的是 calls，不是网上有没有出去一个请求。
  假对象如果内部又去调真 SDK 或 start_mock，这课就失败了。
  对照 Mockito：mock 掉依赖，单测里不要真的打下游。
- 地址题如果也去调用模型，错在没有资料还去问。
  模型会编一个地址。这是第 35 课的拒答：没有命中就不要打模型。
  调用次数会变成 1，assert client.calls == 0 会失败。
  就算回答碰巧是「不知道」，也已经花了一次调用，账单和幻觉都没挡住。
  拒答必须写在 create 之前。
"""

from __future__ import annotations

from types import SimpleNamespace


class FakeClient:
    """形状上有 chat.completions.create。业务代码不用写 if 测试。"""

    def __init__(self) -> None:
        self.calls = 0  # 真 SDK 没有这个字段。测试用它数打了几次。
        # 三个点号还是这一个对象。client.chat.completions.create 会进下面的 create。
        self.chat = self
        self.completions = self

    async def create(self, **kwargs) -> SimpleNamespace:
        """假的创建。async 是因为业务代码写了 await。kwargs 接住 model、messages，这里不用。"""

        self.calls += 1
        message = SimpleNamespace(content="回声")
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        return SimpleNamespace(choices=[choice], usage=usage)


async def answer(client: FakeClient, question: str) -> str:
    """地址题直接返回。下面的 await 不会执行，calls 不加。"""

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
    assert address == "不知道"  # 失败会抛 AssertionError，脚本非 0 退出。
    assert client.calls == 0

    text = await answer(client, "你好")
    assert text == "回声"
    assert client.calls == 1  # 只有这一问进了 create。
    print("地址", address, "调用", 0)
    print("你好", text, "调用", client.calls)


def main() -> None:
    import asyncio

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
