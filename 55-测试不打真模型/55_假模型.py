"""第 55 课示例：测试里的模型是假的。地址题不调用它。

对照 Mockito。CI 里不要打付费接口，也不要指望网络。
这里不用 pytest 启动器。断言写在脚本里，python 直接跑。pytest 只是把这些断言收进测试方法。
"""

from __future__ import annotations

# SimpleNamespace：一个只有属性的空对象。对照一个没写类、临时用来装公开字段的 holder。
# 测试要的是 resp.choices[0].message.content 这条路径走得通，不是真的 SDK 类型。
from types import SimpleNamespace


class FakeClient:
    """形状上有 chat.completions.create，这样业务代码不用为测试改写法。

    对照 Mockito 的 mock。这里不用库，是因为要看懂「鸭子类型」：
    不实现某个接口，只要点出来的属性路径在，调用方就能跑。Java 必须先有接口或基类。
    """

    def __init__(self) -> None:
        self.calls = 0  # 测试要断言的次数。真 SDK 没有这个字段，它只属于假对象。
        # client.chat.completions.create 会走到下面的 create。
        # 把 chat 和 completions 都指回自己，三个点号还是这一个对象。对照一个 mock 的链式调用都返回自己。
        self.chat = self
        self.completions = self

    async def create(self, **kwargs) -> SimpleNamespace:
        """假的 chat.completions.create。async 是因为业务代码写了 await。

        **kwargs 把 model、messages 这些关键字参数收成一个 dict，然后故意不用。
        对照方法接受 Map，测试不关心里面的提示词。真要断言「传入了哪一句」，就要读 kwargs。
        """
        self.calls += 1  # 每进一次加一。地址题如果也进了这里，下面的断言会失败。
        # 测试不关心文采。固定一句，并留下 usage，好让调用方能读 token。
        message = SimpleNamespace(content="回声")  # message.content 能点出来。对照一个 public 字段。
        choice = SimpleNamespace(message=message)  # choice.message 再点一层。
        usage = SimpleNamespace(prompt_tokens=1, completion_tokens=2)
        # choices 是列表，调用方取 [0]。和真 SDK 的路径一致，类型不是同一个类。
        return SimpleNamespace(choices=[choice], usage=usage)


async def answer(client: FakeClient, question: str) -> str:
    """地址题直接拒答，不碰 client。其他问题才调用模型。

    这是被测的业务函数，不是测试框架。分支写在你的代码里，假对象只负责计数。
    """
    if "地址" in question:
        # in 是子串。含「地址」就返回，下面的 await 不会执行，calls 不加。
        return "不知道"
    resp = await client.chat.completions.create(
        model="mock-chat",  # 假的 create 用 **kwargs 接住，不会因为多了这个参数而报错。
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content  # 假对象上这条路径是我们在 create 里搭好的。


async def main_async() -> None:
    client = FakeClient()  # 每个用例自己的假对象。calls 从 0 开始，不和别的测试共享。
    address = await answer(client, "公司地址在哪")
    # 拒答之后，调用次数必须仍是 0。这是这课要守住的断言。
    # assert 失败抛 AssertionError，脚本以非 0 退出。对照 JUnit 的 assertEquals。
    # python -O 会丢掉 assert。教学脚本这样写可以，正式测试用 pytest 的 assert，同样会被 -O 丢掉，所以 CI 不要加 -O。
    assert address == "不知道"
    assert client.calls == 0

    text = await answer(client, "你好")
    assert text == "回声"
    assert client.calls == 1  # 只有这一问打到了 create。地址那问没有。
    print("地址", address, "调用", 0)
    print("你好", text, "调用", client.calls)


def main() -> None:
    # import 写在函数里。Java 不能把 import 挪进方法。这里只有直接运行才需要 asyncio.run。
    import asyncio

    asyncio.run(main_async())  # 新建事件循环，跑完上面的协程。断言失败会从这里抛出来。


if __name__ == "__main__":
    main()
