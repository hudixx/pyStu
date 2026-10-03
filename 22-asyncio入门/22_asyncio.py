"""第 22 课示例：async def / await / TaskGroup / 堵住事件循环。

对照 Java：
- asyncio.run ≈ 启动 Netty 事件循环，跑完一个入口任务再退出
- async def 返回 coroutine ≈ 得到 Mono / CompletableFuture，还没执行
- await ≈ 把等待让出去，不是再开一条线程
- TaskGroup ≈ Java 21 StructuredTaskScope
- time.sleep 在协程里 ≈ 在 event loop 线程里 Thread.sleep

四个 sleep(0.2)：串行 ≈ 0.8s；TaskGroup ≈ 0.2s，但只有一条线程。
"""

from __future__ import annotations

# asyncio：事件循环、协程、TaskGroup 都在这个标准库里。对照 Netty EventLoop。
import asyncio
# time：本课用来「计时」和「错误示范 time.sleep」。计时用 perf_counter，睡眠用 asyncio.sleep。
import time


async def wait_one(name: str, seconds: float) -> str:
    """异步等待。await sleep 会把这几秒让给事件循环上的其它任务。

    async def：调用它不会马上执行函数体，只造出一个 coroutine 对象。
    对照：Mono.fromCallable(...) 得到的是发布者，还没订阅、不算跑过。
    """
    # asyncio.sleep 不是 time.sleep：它登记「N 秒后再叫醒我」，然后交出控制权。
    # 事件循环趁这段空档去跑别的 Task。对照：不要在 Netty 线程里 Thread.sleep。
    await asyncio.sleep(seconds)
    return name  # 被 await / TaskGroup 的人拿到的就是这个返回值


async def serial() -> list[str]:
    """一个等完再等下一个。四个 0.2s 大约 0.8s。

    有 TaskGroup 却在 for 里一个一个 await，照样是串行。并发的关键是「先都挂上，再一起等」。
    """
    out: list[str] = []  # 注解 list[str] 对照 List<String>，运行时不检查
    for name in ("a", "b", "c", "d"):
        # await 会等 wait_one 整段结束才进下一次循环，所以时间相加。
        out.append(await wait_one(name, 0.2))
    return out


async def concurrent() -> list[str]:
    """四个一起等。总时间大约 0.2s，仍然只有一条线程。"""
    # async with：TaskGroup 本身也是异步上下文。进入 with 开始接任务，离开 with 时全部收齐。
    # 对照 try (var scope = new StructuredTaskScope.ShutdownOnFailure()) { ... scope.join(); }
    async with asyncio.TaskGroup() as tg:
        # create_task：把协程交给事件循环调度，马上返回 Task，并不等它结束。
        # 四个 Task 几乎同时开始 sleep，所以总时间 ≈ max 而不是 sum。
        tasks = [tg.create_task(wait_one(name, 0.2)) for name in ("a", "b", "c", "d")]
    # 离开 with 时全部结束（成功或失败）。失败会在离开 with 时抛，到不了下一行。
    # result() 取返回值；若任务里抛过异常，这里会再抛。对照 Future.get()。
    return [t.result() for t in tasks]


async def blocked_pair() -> None:
    """错误示范：协程里 time.sleep，两个 0.3s 会变成约 0.6s。"""

    async def stuck() -> None:
        # 堵住整条事件循环线程。另一个 stuck 根本跑不起来，只能排队。
        # 写成 async def 没用：函数体里没有 await，控制权交不出去。
        time.sleep(0.3)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(stuck())
        tg.create_task(stuck())  # 看起来并发，实际被第一个 sleep 卡住，时间相加


async def yielded_pair() -> None:
    """正确：两个 0.3s 重叠，大约 0.3s。"""

    async def loose() -> None:
        # 有 await，事件循环可以在这 0.3s 里跑另一个 loose。
        await asyncio.sleep(0.3)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(loose())
        tg.create_task(loose())


def timed(label: str, seconds: float) -> None:
    """统一打印秒数，方便对数量级。普通 def：里面没有 await，不能也不该写成 async。"""
    print(f"{label}: {seconds:.2f}s")


def main() -> None:
    """入口是普通 def。真正跑协程靠 asyncio.run，不要在已经在跑的循环里再 run。"""
    # 只调用、不 await：得到 coroutine 对象。对照 new 了一个没订阅的 Mono。
    leftover = wait_one("漏掉 await", 0.1)
    print("没 await 时拿到的是", type(leftover).__name__)  # 一般是 coroutine
    # 不 close 的话，解释器退出时会 RuntimeWarning: coroutine was never awaited。
    leftover.close()

    t0 = time.perf_counter()  # 高精度计时，对照 System.nanoTime()
    # asyncio.run：新建事件循环，跑完 serial()，关掉循环。脚本入口用这个。
    print("串行结果 =", asyncio.run(serial()))
    timed("串行 4×0.2s", time.perf_counter() - t0)

    t0 = time.perf_counter()
    print("并发结果 =", asyncio.run(concurrent()))
    timed("TaskGroup 4×0.2s", time.perf_counter() - t0)

    t0 = time.perf_counter()
    asyncio.run(blocked_pair())
    timed("错误：两个 time.sleep(0.3) 放进 TaskGroup", time.perf_counter() - t0)

    t0 = time.perf_counter()
    asyncio.run(yielded_pair())
    timed("正确：两个 asyncio.sleep(0.3)", time.perf_counter() - t0)


if __name__ == "__main__":
    main()
