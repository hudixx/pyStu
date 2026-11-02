"""验收第 1 课：流式拼成一句，JSON 收成对象，超时再试一次。

对照官方 SDK 的三件事，但客户端是假的。不访问公网，不读 API 密钥。
第一次 stream 抛 TimeoutError。第二次才吐出两段。调用次数应是 2。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from pydantic import BaseModel


class Days(BaseModel):
    """模型答应返回的 JSON。只有一个整数栏。对照一个 DTO。"""

    days: int


class FakeClient:
    """没有网络。第一次调用故意超时，从第二次起才给出两段文本。"""

    def __init__(self) -> None:
        self.calls = 0  # 测试要看的次数。真 SDK 没有这个字段。

    async def stream(self, question: str) -> AsyncIterator[str]:
        """异步生成器。调用方用 async for 一段段拿。"""

        self.calls += 1
        if self.calls == 1:
            # 在 yield 之前抛。调用方一段都还没拿到，这次不算半句成功。
            raise TimeoutError("超时")
        yield "退"  # 第一段。单独还不是一句。
        yield "款"


async def ask(client: FakeClient) -> str:
    """最多试两次。第一次超时就再来一次。两次都失败才返回「失败」。"""

    for _attempt in range(2):  # 下划线开头：这个循环变量不用。
        try:
            parts: list[str] = []
            async for part in client.stream("退款"):
                parts.append(part)
            return "".join(parts)  # 「退」和「款」拼成「退款」。
        except TimeoutError:
            continue  # 这次作废，进入下一次尝试。
    return "失败"


def read_days(raw: str) -> int:
    """把模型给的 JSON 收成对象，再取出天数。坏 JSON 会抛，不在这里吞掉。"""

    # model_validate_json 是 pydantic 第 2 版的方法。对照 ObjectMapper.readValue。
    return Days.model_validate_json(raw).days


async def main() -> None:
    client = FakeClient()
    text = await ask(client)
    print("重试后", text)
    print("天数", read_days('{"days": 7}'))
    print("调用", client.calls)


if __name__ == "__main__":
    asyncio.run(main())
