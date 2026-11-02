"""选修 B6 第 1 课：先量出谁最慢，再改。不要凭感觉挑函数。

对照 JFR。cProfile 把程序跑在它下面，每个函数花了多少自身时间都能对上。
本课只打印函数名，不打印秒数。秒数每次会浮动，名字不会。
"""

from __future__ import annotations

import cProfile
import pstats


def fast() -> int:
    """几乎不干活。用来对照。"""

    return 1


def slow() -> int:
    """把一段循环跑完。这段才是时间花掉的地方。"""

    total = 0
    for i in range(200_000):  # 下划线只方便读，值还是二十万。
        total += i
    return total


def hottest(names: set[str]) -> str:
    """在这几个名字里，找出自身时间最长的那个。"""

    profile = cProfile.Profile()
    profile.enable()  # 从这里开始记。之前定义函数的时间不算。
    fast()
    slow()
    profile.disable()
    best_name = ""
    best_time = -1.0
    # stats 的键是 (文件, 行号, 函数名)。值是五元组：
    # 原始调用次数、总调用次数、自身时间、总时间、谁调用了它。
    for (_filename, _line, name), (_cc, _nc, tottime, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name in names and tottime > best_time:
            best_name = name
            best_time = tottime
    return best_name


def main() -> None:
    print("最慢", hottest({"fast", "slow"}))


if __name__ == "__main__":
    main()
