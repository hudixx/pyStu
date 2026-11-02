"""选修 B6 第 2 课：自身时间不含叫出去的函数。总时间含。

outer 几乎只是去调用 inner。它的自身时间很短，总时间把 inner 算进来，所以更长。
inner 自己做循环，没有再往下叫，自身时间和总时间分不开。

对照看一份剖析报告：父函数的总时间大，不代表该改父函数。
py-spy 是另一件工具。进程已经在跑、不能重启时，从外面采样看它的栈。
本课不安装 py-spy。Windows 上它经常要管理员权限。练习仍用 cProfile。
"""

from __future__ import annotations

import cProfile
import pstats


def inner() -> int:
    """时间花在这里。它不再调用别的函数。"""

    total = 0
    for i in range(200_000):
        total += i
    return total


def outer() -> int:
    """自己几乎不干活，只把 inner 叫起来。"""

    return inner()


def relation(tottime: float, cumtime: float) -> str:
    """总时间明显大于自身时间，就说明时间在它叫出去的函数里。"""

    if cumtime > tottime + 1e-9:  # 浮点不要用 ==。差一点点不算「大于」。
        return "自身小于总时间"
    return "自身等于总时间"


def report() -> dict[str, str]:
    """剖析一次 outer()，记下 outer 和 inner 各自的两种时间。"""

    profile = cProfile.Profile()
    profile.enable()
    outer()
    profile.disable()
    found: dict[str, str] = {}
    for (_filename, _line, name), (_cc, _nc, tottime, cumtime, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name in {"outer", "inner"}:
            found[name] = relation(tottime, cumtime)
    return found


def main() -> None:
    found = report()
    print("outer", found["outer"])
    print("inner", found["inner"])


if __name__ == "__main__":
    main()
