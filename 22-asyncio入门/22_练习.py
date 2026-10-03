import asyncio
import time


async def wait_one(name: str = "1") -> str:
    await asyncio.sleep(0.2)
    return name

async def sleep_one(name: str = "1") -> str:
    time.sleep(0.2)
    return name

async def serial() -> list:
    arr = ["a", "b", "c", "d"]
    out: list[str] = []
    for x in arr:
        out.append(await wait_one(x))
    return out

async def concurrent() -> list[str]:
    arr = ["a", "b", "c", "d"]
    tasks: list = []
    async with asyncio.TaskGroup() as tg:
        # 下面这行不行（即使语法能过，运行也会炸）：
        # return [f.result() for f in [tg.create_task(wait_one(x)) for x in arr]]
        #
        # 原因：TaskGroup 是「离开 with 时才等全部结束」。
        # 这行写在 with 里面，create_task 刚把任务挂上，立刻 .result()——任务还在 sleep，
        # 结果还没 set，会 InvalidStateError（对照 Future.get() 在任务没跑完时调用）。
        # return 虽然也会触发 with 的收尾，但 list 推导式里的 .result() 更早求值，等不到收尾。
        #
        # 正确拆成两步：with 里只 create_task；with 结束之后再 .result()。
        # 若想一行拿结果，用 gather：return list(await asyncio.gather(*(wait_one(x) for x in arr)))
        for x in arr:
            tasks.append(tg.create_task(wait_one(x)))
    return [f.result() for f in tasks]

async def pair(fun) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fun())
        tg.create_task(fun())





def main() -> None:
    t0 = time.perf_counter()
    print("串行结果 =", asyncio.run(serial()))
    print("串行时间：", time.perf_counter() - t0)
    t0 = time.perf_counter()
    print("并行结果 =", asyncio.run(concurrent()))
    print("并行时间：", time.perf_counter() - t0)
    t0 = time.perf_counter()
    asyncio.run(pair(wait_one))
    print("测试时间：", time.perf_counter() - t0)
    t0 = time.perf_counter()
    asyncio.run(pair(sleep_one))
    print("测试时间2：", time.perf_counter() - t0)


if __name__ == "__main__":
    main()

    """
    题 2：看示例里「两个 time.sleep」和「两个 asyncio.sleep」的秒数。
    - 错误那组会变成约 0.6s（两个 0.3s 相加）。本文件 pair(sleep_one) 两个 0.2s 约 0.4s，同一现象。
    - TaskGroup 救不了 time.sleep：它卡住的是整条事件循环线程，没有 await 就把控制权交回去，
      组里其它任务根本排不上号。对照在 Netty event loop 里 Thread.sleep。

    题 3：asyncio、ThreadPoolExecutor、Java WebFlux。
    - 相同 1：都能让多次 IO 等待重叠，四个 0.2s 可以约 0.2s 跑完，不是必须 0.8s。
    - 相同 2：都不是「开四条线程做 CPU 并行」；本质是等 IO，不是把 Python/Java 字节码真并行算完。
    - 不同：asyncio / WebFlux 默认一条事件循环线程，在 await / 订阅处切换；
      ThreadPoolExecutor 是 N 条线程，操作系统帮你切换，每条线程可以同步阻塞。
    - 普通 def 里不能写 await，语法直接报错。必须写在 async def 里。
    """