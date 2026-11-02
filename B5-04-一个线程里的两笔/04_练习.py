from __future__ import annotations

import asyncio
import threading
import contextvars


local = threading.local()
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")

async def worker(name: str) -> None:
    local.value = name
    trace_id.set(name)
    await asyncio.sleep(0)
    print(name , "local", getattr(local, "value", "-"), "context", trace_id.get())

async def run() -> None:
    await asyncio.gather(worker("甲"), worker("乙"))

def main() -> None:
    asyncio.run(run())

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出