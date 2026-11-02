"""选修 B5 第 3 课参考答案。题 1 过了。题 2 写在下面。

运行 03_练习.py 看到：

入口 R-9
下游 R-9
结束后 -

用的是 contextvars，不是模块里的一个普通字符串。
下游没有参数，读的是 trace_id.get()。
set 的 token 交给了 finally 里的 reset。handle 返回后再读，是默认的「-」。

from 和 __future__ 之间多了一个空格。本课 ruff 没报，不影响这三行。

题 2：
- 模块里的一个字符串，整个进程只有那一格。两笔叠在一起，后写的盖掉先写的。
  ContextVar 这个对象全进程一份，值跟着当前上下文走。下一课把两笔放在同一条线程上。
- reset 放在 finally，是因为中间抛了异常也要还。只写在成功之后，异常一出就走不到，
  后面没 set 的代码会读到 R-9。对照 MDC.clear() 放在 finally。
"""

from __future__ import annotations

import contextvars

trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


def downstream() -> None:
    print("下游", trace_id.get())


def handle(request_id: str) -> None:
    token = trace_id.set(request_id)
    try:
        print("入口", trace_id.get())
        downstream()
    finally:
        trace_id.reset(token)


def main() -> None:
    handle("R-9")
    print("结束后", trace_id.get())


if __name__ == "__main__":
    main()
