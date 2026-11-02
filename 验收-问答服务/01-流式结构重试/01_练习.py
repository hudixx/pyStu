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
        print("进入")
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("超时")
        yield "七"
        yield "天"

async def ask(client: FakeClient) -> str:
    for _attempt in range(4):
        try:
            parts: list[str] = []
            stream = client.stream("退款")
            async for part in stream:
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

#  题2不知道，请在参考答案的注释中个给出