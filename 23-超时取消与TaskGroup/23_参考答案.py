"""第 23 课参考答案。题 1 / 2 能跑通：超时打印「超时」，TaskGroup 打出 x 和 y。

你额外加了「失败」那一组，方向对：一个 RuntimeError，兄弟被取消，
ExceptionGroup 里能看到 RuntimeError。

差在 wait_one 里：
    except asyncio.CancelledError:
        print(...)
        pass          # 把取消吞掉了
必须再 raise。CancelledError 是 BaseException，except Exception 抓不住；
你特意抓住再 pass，等于告诉 TaskGroup「这个任务正常结束了，返回 None」。
对照 Java：catch (InterruptedException) 之后要保留中断状态，不能当没事。

题 3：Java future.cancel(true) 和 asyncio 取消。
- 相同：都是协作式，不是 Thread.stop。对方要在可取消的等待点醒来
  （Java 可中断阻塞 / interrupted 标志；asyncio 在 await 处收到 CancelledError）。
- 不同：Java 是发 interrupt，线程还在，代码要自己检查；
  asyncio 是往协程里丢 CancelledError（BaseException），默认就会结束当前 await。
- 不要 except BaseException: pass：连取消和 KeyboardInterrupt 都吞掉，
  超时、TaskGroup 取消、Ctrl+C 全部失效。清理放 finally，不要把取消当业务异常吃掉。
"""

from __future__ import annotations

import asyncio


async def slow() -> str:
    """1 秒后才返回。外层 timeout(0.2) 会取消它，到不了 return。"""
    await asyncio.sleep(1)
    return "ok"


async def wait_one(name: str) -> str:
    """睡 0.2 秒后返回 name。题 2 不必制造失败。"""
    await asyncio.sleep(0.2)
    return name


async def main() -> None:
    try:
        async with asyncio.timeout(0.2):
            print(await slow())  # 正常跑不到
    except TimeoutError:
        print("超时")

    async with asyncio.TaskGroup() as tg:
        tx = tg.create_task(wait_one("x"))
        ty = tg.create_task(wait_one("y"))
    print(tx.result())
    print(ty.result())


if __name__ == "__main__":
    asyncio.run(main())
