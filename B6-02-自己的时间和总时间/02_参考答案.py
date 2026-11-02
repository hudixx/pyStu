"""选修 B6 第 2 课参考答案。题 1 过了。题 2 写在下面。

运行 02_练习.py 看到：

pack 自身小于总时间
fill 自身等于总时间

fill 做二十万次加法。pack 调用了它。比较用的是总时间比自身时间大过 1e-9，没有用 ==。

pack 写成了调用 fill()，没有 return。题目写的是 return fill()。
剖析看的是这次调用，返回值没有人用，所以两种时间仍然对。

那一行 for 长过 100。ruff 报了 E501。
relation 的两个参数之间少了一个空格。return 后面多了一个空格。

题 2：
- pack 的总时间大，是因为 fill 的循环算在里面。pack 自己几乎没有语句。
  先改 pack，循环还在 fill 里。自身时间和总时间分开，就是为了看到该看孩子。
- 已经在跑、不能重启的进程，cProfile 的记录里没有它。
  cProfile 只记下 enable 和 disable 之间、这次启动的调用。
  py-spy 从外面看它现在的栈，不用在剖析器下面重新启动。本课不安装它。
"""

from __future__ import annotations

import cProfile
import pstats


def fill() -> int:
    total = 0
    for i in range(200_000):
        total += i
    return total


def pack() -> int:
    return fill()


def relation(tottime: float, cumtime: float) -> str:
    if cumtime > tottime + 1e-9:
        return "自身小于总时间"
    return "自身等于总时间"


def report() -> dict[str, str]:
    profile = cProfile.Profile()
    profile.enable()
    pack()
    profile.disable()
    found: dict[str, str] = {}
    stats = pstats.Stats(profile).stats
    for (_filename, _line, name), (_cc, _nc, tottime, cumtime, _callers) in stats.items():
        if name in {"pack", "fill"}:
            found[name] = relation(tottime, cumtime)
    return found


def main() -> None:
    found = report()
    print("pack", found["pack"])
    print("fill", found["fill"])


if __name__ == "__main__":
    main()
