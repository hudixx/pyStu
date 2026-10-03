"""第 22 课参考答案。题 1 数量级对：串行约 0.8s，TaskGroup 约 0.2s。

你多写的 pair(wait_one) / pair(sleep_one) 正好对应示例里那组对比，方向对。

TaskGroup 里不能一边 create_task 一边 .result()：离开 with 才等齐。
对照 Future.get() 写在 StructuredTaskScope.join() 之前。想一行拿结果用 gather。

题 2：
- 错误那组（两个 time.sleep(0.3)）会变成约 0.6s，是相加不是重叠。
- TaskGroup 救不了 time.sleep：它卡住整条事件循环线程，没有 await 就把
  控制权交回去，组里其它任务排不上号。对照在 Netty event loop 里 Thread.sleep。

题 3：asyncio、ThreadPoolExecutor、Java WebFlux。
- 相同 1：都能让多次 IO 等待重叠，四个 0.2s 可以约 0.2s 跑完。
- 相同 2：都不是「开四条线程把 CPU 算力叠上去」；本质是等 IO。
- 不同：asyncio / WebFlux 默认一条事件循环线程，在 await / 订阅处切换；
  ThreadPoolExecutor 是 N 条线程，操作系统帮你切，每条可以同步阻塞。
- 普通 def 里不能写 await，语法直接报错。必须写在 async def 里。
"""

from __future__ import annotations

import asyncio
import time


async def wait_one(name: str) -> str:
    """await sleep 会把这 0.2 秒让出去。只调用不 await，拿到的是 coroutine。"""
    await asyncio.sleep(0.2)
    return name


async def serial() -> list[str]:
    """for 里一个一个 await，四个 0.2s 相加约 0.8s。"""
    out: list[str] = []
    for name in ("a", "b", "c", "d"):
        out.append(await wait_one(name))
    return out


async def concurrent() -> list[str]:
    """四个一起挂上，离开 with 时才等齐。总时间约 0.2s。"""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(wait_one(name)) for name in ("a", "b", "c", "d")]
    return [t.result() for t in tasks]


def main() -> None:
    t0 = time.perf_counter()
    print("串行结果 =", asyncio.run(serial()))
    print(f"串行: {time.perf_counter() - t0:.2f}s")

    t0 = time.perf_counter()
    print("并发结果 =", asyncio.run(concurrent()))
    print(f"TaskGroup: {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    main()
