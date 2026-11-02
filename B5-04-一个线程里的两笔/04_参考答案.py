"""选修 B5 第 4 课参考答案。题 1 过了。题 2 写在下面。选修 B5 到这里结束。

运行 04_练习.py 看到：

甲 local 乙 context 甲
乙 local 乙 context 乙

甲排在乙前面交给 gather。两笔都先写下自己的名字，再 await sleep(0)。
甲让出之后，乙把 local.value 写成了乙。甲回来时 local 已经是乙，context 仍是甲。

ContextVar("trace_id",default="-") 逗号后面少了一个空格。
print(name , "local" 逗号前面多了一个空格。本课 ruff 没报，不影响这两行。

题 2：
- 只有一条线程，local 还是串了，因为两笔任务轮流用这一条线程，local 只有一格。
  甲让出的空档里，乙写的是同一格。contextvars 在任务创建时复制一份，乙的 set 改不到甲的那份。
- 只有一笔任务时，await asyncio.sleep(0) 之后 local 还是它自己写的值。
  await 不换线程。没有另一笔在空档里改同一格，就不会串。
"""

from __future__ import annotations

import asyncio
import contextvars
import threading

local = threading.local()
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


async def worker(name: str) -> None:
    local.value = name
    trace_id.set(name)
    await asyncio.sleep(0)
    print(name, "local", getattr(local, "value", "-"), "context", trace_id.get())


async def run() -> None:
    await asyncio.gather(worker("甲"), worker("乙"))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
