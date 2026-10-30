"""选修 B5 第 3 课：同一个请求的号，下游不用参数也能读到。用完要还回去。

对照 MDC 或 Sleuth 的 traceId。Java 里它挂在当前线程上，请求结束要 clear。
Python 这里用 contextvars。不要用模块级的一个字符串：整个进程只有那一格，两笔会互相盖掉。
下一课看一条线程上的两个任务。这一课先把「放上、读到、还回去」写对。
"""

from __future__ import annotations

import contextvars  # 一份「当前上下文」里的变量。对照 MDC，但复制的是上下文，不是一格全局字符串。


# default 是还没 set、或者已经 reset 之后读到的值。不是空字符串。
# 这一行在 import 本文件时就执行，全进程一份 ContextVar 对象。对照 public static final 那个槽。
# 槽是一个，各段代码读到的值可以不同。不要改成 trace_id = "-"，那样全进程只有一格，后写的盖掉先写的。
# ContextVar[str] 对照这个槽里放的是字符串。冒号是类型标注，等号两边有空格，和函数调用里的关键字参数不是同一种写法。
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


def downstream() -> None:
    """不接收请求号。谁调用它，它读的是当前这份上下文。

    逻辑：只 get 一次并打印。参数列表是空的，调用方不用把 request_id 传进来。
    若 handle 已经 set 过，这里打印的就是那一笔的号。还没 set，打印 default 的「-」。
    """

    print("下游", trace_id.get())  # get() 没有参数。读的是「当前上下文」里的值，不是函数参数。


def handle(request_id: str) -> None:
    """这一笔开始时放上号，结束时一定还回去。中间出了错也要还。

    逻辑：
    1. set 把号放进当前上下文，并留下 token。token 是「放之前的状态」，不是号本身。
    2. 打印入口，再调用 downstream。下游没有收到 request_id 这个参数。
    3. finally 里 reset(token)。正常结束和中途抛异常都会走到。
    """

    token = trace_id.set(request_id)  # set 的返回值留给 reset。不要丢掉。
    # set 的返回值不是字符串。丢掉它，后面就无法精确回到这一笔之前的值。
    try:
        print("入口", trace_id.get())  # 刚 set 过，应和 request_id 相同。
        downstream()  # 没有把 request_id 传进去。
    finally:
        # 对照 MDC.clear() 放在 finally。不 reset，后面没 set 的代码会读到这一笔的号。
        # reset 用的是 set 交回来的 token，不是再传一次 "T-1"。对照把 MDC 恢复成 set 之前的样子。
        trace_id.reset(token)


def main() -> None:
    """走一笔 T-1，再在外面读一次，确认号已经还回去了。

    入口和下游都应打印 T-1。结束后这一行应打印 default 的「-」，不是 T-1，也不是空串。
    """

    handle("T-1")
    print("结束后", trace_id.get())  # 已经 reset，回到 default 的「-」。


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 请求号放进上下文之后，下游不用加参数也能 get 到。这不是全局变量。
# 用完必须 reset，而且放在 finally 里。不还回去，后面无关的代码会读到上一笔的号。
# 模块顶上若只放一个字符串，整个进程共用那一格，两笔会互相盖掉。ContextVar 是槽，值跟当前上下文走。
