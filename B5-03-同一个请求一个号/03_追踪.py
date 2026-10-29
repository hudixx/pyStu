"""选修 B5 第 3 课：同一个请求的号，下游不用参数也能读到。用完要还回去。

对照 MDC 或 Sleuth 的 traceId。Java 里它挂在当前线程上，请求结束要 clear。
Python 这里用 contextvars。不要用模块级的一个字符串：整个进程只有那一格，两笔会互相盖掉。
下一课看一条线程上的两个任务。这一课先把「放上、读到、还回去」写对。
"""

from __future__ import annotations

import contextvars

# default 是还没 set、或者已经 reset 之后读到的值。不是空字符串。
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


def downstream() -> None:
    """不接收请求号。谁调用它，它读的是当前这份上下文。"""

    print("下游", trace_id.get())


def handle(request_id: str) -> None:
    """这一笔开始时放上号，结束时一定还回去。中间出了错也要还。"""

    token = trace_id.set(request_id)  # set 的返回值留给 reset。不要丢掉。
    try:
        print("入口", trace_id.get())
        downstream()  # 没有把 request_id 传进去。
    finally:
        # 对照 MDC.clear() 放在 finally。不 reset，后面没 set 的代码会读到这一笔的号。
        trace_id.reset(token)


def main() -> None:
    handle("T-1")
    print("结束后", trace_id.get())  # 已经 reset，回到 default 的「-」。


if __name__ == "__main__":
    main()
