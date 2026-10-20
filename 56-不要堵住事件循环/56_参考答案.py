"""第 56 课参考答案。题 1、题 2 都过。题 3 写在下面。阶段十结束。

跑出来是：
堵住 0.40 秒
让出 0.21 秒
健康 {'status': 'ok'}

两个 await asyncio.sleep(0.2) 用 gather 一起跑，耗时小于 0.35 秒。
健康检查返回 {"status": "ok"}。没有打开数据库，没有创建模型客户端，也没有安装 Docker。

练习里 def 和 main 之间多了一个空格，写成了 def  main。不影响运行。函数名前面只留一个空格，应写成 def main。

题 3：
- time.sleep 写在 async def 里，事件循环会被占住。
  async def 不会把里面的 time.sleep 变成异步。那一行占住当前线程，别的任务进不来。
  两个各睡 0.2 秒的任务会一个接一个，墙上大约 0.40 秒，不是 0.20 秒。
  对照在 Netty 的 IO 线程里 Thread.sleep。要让出，用 await asyncio.sleep。
- vLLM 的上下文长度是容量参数，不是让你去训练模型。
  上下文长度、批大小、量化，决定的是这台推理机器一次能装下多长的输入、
  能同时处理多少请求、要多少显存。对照 JVM 堆大小。
  你的服务通过 HTTP 调用它，不在这里改模型的权重。
  这一阶段不训练模型，也不要求有 GPU。同目录的 Dockerfile 只给看，不必构建。
"""

from __future__ import annotations

import asyncio
import time


async def block() -> None:
    """错误示范。async def 里没有 await，time.sleep 占住当前线程。"""

    time.sleep(0.2)


async def wait() -> None:
    """正确示范。await 会把控制权交回去，两个任务的 0.2 秒可以重叠。"""

    await asyncio.sleep(0.2)


async def elapsed(job) -> float:
    """job 是函数本身。这里调用两次，再一起等。"""

    started = time.perf_counter()
    await asyncio.gather(job(), job())
    return time.perf_counter() - started


def health() -> dict:
    """只回答进程还在。不查库，不打模型。"""

    return {"status": "ok"}


async def main_async() -> None:
    # 传入函数，不要写成 elapsed(block())。加了括号就是已经创建一个协程。
    blocked = await elapsed(block)  # 两个 time.sleep 串成一队，大约 0.40 秒。
    waited = await elapsed(wait)  # 两个 asyncio.sleep 重叠，大约 0.20 秒，应小于 0.35。
    print(f"堵住 {blocked:.2f} 秒")
    print(f"让出 {waited:.2f} 秒")
    print("健康", health())


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
