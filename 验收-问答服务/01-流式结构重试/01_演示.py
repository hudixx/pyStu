"""验收第 1 课：流式拼成一句，JSON 收成对象，超时再试一次。

对照官方 SDK 的三件事，但客户端是假的。不访问公网，不读 API 密钥。
第一次 stream 抛 TimeoutError。第二次才吐出两段。调用次数应是 2。
"""

# 推迟注解求值。list[str]、AsyncIterator[str] 在 import 时不会被执行。
from __future__ import annotations

import asyncio  # asyncio.run 把下面的 async def 放进事件循环跑完。对照自己建循环再 join。
# AsyncIterator 是类型标注：这个异步生成器会一段段交出 str。对照一个会多次给出值的异步方法，不是返回 List。
from collections.abc import AsyncIterator

from pydantic import BaseModel  # DTO 基类。model_validate_json 会解析并校验。对照 Jackson 读进一个类。


class Days(BaseModel):
    """模型答应返回的 JSON。只有一个整数栏。对照一个 DTO。

    字段 days 写成 days: int，JSON 里就要有整数 "days"。缺字段或不是整数，校验会抛，不在这里吞。
    """

    days: int  # 类型标注加字段名。pydantic 用它生成校验。对照一个 public int days。


class FakeClient:
    """没有网络。第一次调用故意超时，从第二次起才给出两段文本。

    真 SDK 的 stream 会一段段交出模型文字。这里用 yield 假装那些段，并用 calls 数被调用了几次。
    """

    def __init__(self) -> None:
        """构造时把调用次数清零。每个 FakeClient 自己数自己的，不和别的实例共用。"""

        self.calls = 0  # 测试要看的次数。真 SDK 没有这个字段。

    async def stream(self, question: str) -> AsyncIterator[str]:
        """异步生成器。调用方用 async for 一段段拿。

        逻辑：
        1. 每次进入都把 calls 加 1。question 本课不用，留着是为了和真接口的「传入问题」形状一样。
        2. 第一次直接抛 TimeoutError。还没有任何 yield，调用方一段都没拿到。
        3. 从第二次起，先交出「退」，再交出「款」。两段要调用方自己拼。
        async def 里有 yield，所以这是异步生成器，不是普通的返回一个列表。
        """

        self.calls += 1  # 先记账。超时也算一次调用，因为请求已经发出去了。
        if self.calls == 1:
            # 在 yield 之前抛。调用方一段都还没拿到，这次不算半句成功。
            # raise 对照 throw。TimeoutError 是内置异常，表示超时。第 30 课的 APITimeoutError 是 SDK 包的那一种。
            raise TimeoutError("超时")
        yield "退"  # 第一段。单独还不是一句。
        # yield 把这一小段交给 async for，然后函数停在这里。循环再来要下一段，才继续往下。
        # 对照把 Flux 里的一个元素交出去，不是 return。return 会结束整个生成器。
        yield "款"


async def ask(client: FakeClient) -> str:
    """最多试两次。第一次超时就再来一次。两次都失败才返回「失败」。

    逻辑：
    1. range(2) 只会走进循环两次，下标 0 和 1。循环变量故意不用。
    2. 每次新开一个 parts 列表，用 async for 把流里的每一段 append 进去。
    3. 流正常结束就把各段用空串拼起来返回。拼成功就不再试下一次。
    4. 只抓 TimeoutError。抓到就 continue，这一次的 parts 丢掉。
    5. 两次都在超时里结束，循环跑完，返回「失败」。
    """

    for _attempt in range(2):  # 下划线开头：这个循环变量不用。
        # range(2) 产生 0、1。对照 for (int i = 0; i < 2; i++)，但这里不读 i。
        try:
            parts: list[str] = []  # 这一次尝试自己的片段。上次超时留下的列表已经丢了，这里是新的。
            async for part in client.stream("退款"):
                # async for：向异步生成器要下一段。没有就挂起。对照遍历一个 Flux，但是不堵死事件循环。
                # 第一次 stream 在 yield 前就抛，这个循环一次都不会进，直接跳到 except。
                parts.append(part)  # append 在末尾加一段。对照 list.add。
            return "".join(parts)  # 「退」和「款」拼成「退款」。
            # "".join(列表) 用空串把各段粘起来。对照 String.join("", parts)。比在循环里 text = text + part 更合适。
        except TimeoutError:
            continue  # 这次作废，进入下一次尝试。
            # continue 跳过这一轮剩下的代码，回到 for 的下一次。对照 continue。不要在这里 return。
    return "失败"  # 只有两次都超时才走到这里。有一次拼成功，上面已经 return 了。


def read_days(raw: str) -> int:
    """把模型给的 JSON 收成对象，再取出天数。坏 JSON 会抛，不在这里吞掉。

    逻辑：用 Days 的模型去解析整段文本。成功就读 .days 这个整数。缺字段、类型不对、根本不是 JSON，都抛出去。
    """

    # model_validate_json 是 pydantic 第 2 版的方法。对照 ObjectMapper.readValue。
    # 返回的是 Days 对象。再点 .days 取出那个整数。点的是字段，不是 getter。
    return Days.model_validate_json(raw).days


async def main() -> None:
    """造一个假客户端，问一次，再解析一段固定 JSON，最后打印调用次数。

    预期：重试后得到「退款」，天数是 7，调用次数是 2。第一次超时，第二次才吐出两段。
    """

    client = FakeClient()  # calls 从 0 开始。
    text = await ask(client)  # await 等到 ask 这个协程给出字符串。对照 join 一个异步任务。
    print("重试后", text)
    print("天数", read_days('{"days": 7}'))  # 单引号字符串里可以写双引号。这是一段合法 JSON。
    print("调用", client.calls)  # 假对象上的字段。超时那次也加过 1，所以是 2。


if __name__ == "__main__":
    # 直接运行本文件才进这里。asyncio.run 创建事件循环，把 main 跑完，再关掉循环。
    # 不要在另一个 async def 里再套 asyncio.run。
    asyncio.run(main())

# 这个脚本想说明的事：
# 流式是一段段拿，不是等整句。拿齐再用空串拼起来。
# 超时发生在第一段交出来之前，这次不算成功，可以再试。最多两次，两次都失败就返回「失败」，不要无限重试。
# JSON 用 pydantic 收成对象。坏 JSON 让它抛，不要在读天数的函数里吞掉。
