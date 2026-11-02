"""验收第 1 课参考答案。三行结果对了，前面多打了两行。题 2 写在下面。

运行 01_练习.py 看到：

进入
进入
重试后 七天
天数 7
调用 2

题目只要后面三行。七和天拼成七天。JSON 收成了 7。第二次才吐字，所以调用是 2。

stream 里的 print("进入") 每次调用都打。第一次超时、第二次成功，所以是两行。题目没有这两行。
for _attempt in range(4) 是最多四次。题目是两次。这次第二次就成功了，所以调用仍是 2。
若第二次也超时，还会再打第三、第四次。

题 2：
- 超时要在 yield 之前抛，这样这次一段都还没交出去。
  你的 parts 写在每次尝试里面。若先吐出「七」再抛，这次的列表会被丢掉，函数最后仍返回「七天」。
  可是「七」已经从生成器里出来了。真的流式响应撤不回这一段，对方先看到「七」，再看到「七天」。
  若 parts 放在循环外面，拼出来的就是「七七天」。
- 坏 JSON 收成 days = 0，调用方会把它当成「0 天」这种正常答案。
  校验失败要抛出去。0 是一个合法的天数，不是「没解析成」。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from pydantic import BaseModel


class Days(BaseModel):
    days: int


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    async def stream(self, question: str) -> AsyncIterator[str]:
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("超时")
        yield "七"
        yield "天"


async def ask(client: FakeClient) -> str:
    for _attempt in range(2):
        try:
            parts: list[str] = []
            async for part in client.stream("退款"):
                parts.append(part)
            return "".join(parts)
        except TimeoutError:
            continue
    return "失败"


def read_days(raw: str) -> int:
    return Days.model_validate_json(raw).days


async def main() -> None:
    client = FakeClient()
    text = await ask(client)
    print("重试后", text)
    print("天数", read_days('{"days": 7}'))
    print("调用", client.calls)


if __name__ == "__main__":
    asyncio.run(main())
