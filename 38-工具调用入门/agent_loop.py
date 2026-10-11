"""有上限的工具循环。循环是你的代码，不是模型自己在转。

第 40 课讲解这一份。41、43 课 import 它，避免各写一个停不下来的版本。
第 40 课练习要自己写循环，不要 import 本文件。
"""

from __future__ import annotations

import time  # monotonic：不受系统改时间影响的秒表。对照 System.nanoTime，不是 currentTimeMillis。

from mock_tools import tool_specs  # 同一目录。谁 import 本模块，谁的 path 里得有这一课目录。
from todos import run_tool  # 真正改待办的函数。本循环只负责把工单交过去、把回执写回 messages。


class LoopResult:
    """一轮循环的结果。没有用 dataclass，少一个和业务无关的语法点。

    stop:
    - 回答：模型给出了正文，没有再要工具
    - 步数用尽：到了 max_steps 仍想调工具
    - 超时：下一轮模型调用发出去之前，deadline 已经到了

    这是普通类。对照一个手写的不可变 DTO，但这里字段没有改成 private，外面能直接读 result.stop。
    """

    def __init__(self, stop: str, content: str, model_calls: int, tool_runs: int) -> None:
        # __init__ 是构造器。第一个参数 self 是「正在被构造的这个对象」，调用时不要自己传。
        # 对照 Java 构造器没有 this 这个形参，方法体里用 this.x = x。这里要写成 self.x = x。
        self.stop = stop
        self.content = content
        self.model_calls = model_calls  # chat.completions.create 的次数。每一步都是一次请求、一份钱。
        self.tool_runs = tool_runs  # run_tool 的次数。拒绝也算执行过「检查」，因为你的函数跑了。


async def run_loop(
    client,
    messages: list[dict],
    *,
    max_steps: int = 3,
    deadline_s: float | None = None,
) -> LoopResult:
    """在已有的 messages 上转。调用方要先放好 system 和这一轮的 user。

    本函数只追加 assistant 和 tool，不改 messages[0]，不新加 user。
    deadline_s 是「还要不要发下一次模型请求」的闸，不是第 30 课那种把 HTTP 掐断的 timeout。
    已经在飞的那一次会等它返回；返回后若超了，就不再发下一轮。

    星号 * 后面的参数是「只能用名字传」，不能按位置传。
    必须写 run_loop(client, messages, max_steps=3)，不能写 run_loop(client, messages, 3, 1.0)。
    对照：Java 没有这个语法，两个数字参数容易传反；这里用关键字强制分开。
    float | None 对照 @Nullable double，None 表示「不设这道时间闸」。
    """
    if max_steps < 1:
        # 上限至少是 1。0 会让 for 一次都不跑，看起来像坏了而不是被闸拦住。
        # raise 对照 throw。ValueError 是参数不合法。调用方没抓的话，整个程序在这里停。
        raise ValueError("max_steps 至少为 1")

    started = time.monotonic()  # 从某个固定点算起的秒数，float。只用来和自己相减，不要拿去对墙钟。
    model_calls = 0
    tool_runs = 0

    # range(3) 是 0, 1, 2，一共最多 3 轮。下划线 _ 表示「这个序号我不用」。对照 for (int i = 0; i < n; i++) 却不读 i。
    for _ in range(max_steps):
        # is not None：传了 0.0 也算「设了闸」，时间一到就停。不要写成 if deadline_s，0.0 会在布尔判断里被当成假。
        if deadline_s is not None and time.monotonic() - started >= deadline_s:
            # 停在发请求之前。已经执行过的工具结果留在 messages 里，不扔掉。
            return LoopResult("超时", "超时", model_calls, tool_runs)

        model_calls += 1  # 先记账再发请求。这一次如果抛异常，次数已经加上，异常会往外抛，不在这里吞。
        # tools= 每次都带上。这是说明书，不是上一轮的工具结果。结果在 messages 的 role=tool 里。
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=messages,  # 传的是同一个列表对象。前面几轮 append 的内容，这一轮模型都看得到。
            tools=tool_specs(),
            temperature=0,  # 能定住的随机性就定住。假模型不采样，这行是给以后换真模型留的。
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            # 没有工单：这轮的正文就是回答。写回 messages，下一句用户话才不会被旧的工具结果截走。
            # content 仍可能是 None，当成空串，别让打印炸。or 的左边是假值时用右边。
            text = msg.content or ""
            messages.append({"role": "assistant", "content": text})
            return LoopResult("回答", text, model_calls, tool_runs)

        # 本课假模型一次只给一张工单。真模型可能给多张，那时要逐张执行、逐条 role=tool 喂回去。
        call = msg.tool_calls[0]
        # SDK 给的是对象，messages 里要的是 dict。这里按协议把字段抄回去，不能把对象直接 append。
        messages.append(
            {
                "role": "assistant",
                "content": msg.content,  # 有工具调用时通常是 None，原样放回去，不要改写成工具结果。
                "tool_calls": [
                    {
                        "id": call.id,  # 和下面的 tool_call_id 必须是同一个，模型才知道这是哪张工单的回执。
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,  # 仍是字符串，不要先 loads 再塞回来。
                        },
                    }
                ],
            }
        )
        # 同步函数，没有 await。校验、拒绝、改 TODOS 都发生在这一行里面。
        result = run_tool(call.function.name, call.function.arguments)
        tool_runs += 1  # 拒绝也算一次：run_tool 确实跑了，只是没有 append 到 TODOS。
        messages.append(
            {
                "role": "tool",  # 不是 user，也不是 system。工具结果是数据。
                "tool_call_id": call.id,
                "content": result,  # 中文句子，比如「已添加 买牛奶」或「拒绝: ...」。
            }
        )
        # 这一轮不 return。for 回到顶部，用已经追加好的 messages 再问一次模型，让它根据工具结果写给人看的正文。

    # for 正常结束才走到这：每一步都还想调工具，次数被 range 截断。
    # 模型若在 max_steps 之内给出正文，上面已经 return，不会走到这一行。
    return LoopResult("步数用尽", "步数用尽", model_calls, tool_runs)
