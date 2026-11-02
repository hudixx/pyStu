"""选修 B6 第 1 课参考答案。题 1 过了。题 2 写在下面。

运行 01_练习.py 看到：

最慢 milk

milk 做二十万次加法，bread 只 return 1。剖析包住这两次调用，打印的是名字，没有秒数。

key[2] 是函数名，value[2] 是自身时间。这个下标对上了。
五元组的顺序是：原始调用次数、总调用次数、自身时间、总时间、调用者。
下标比拆开名字容易看错。下一课要分自身时间和总时间，用名字更清楚。
best_time 写成了 -1，不是 -1.0。和浮点比大小仍然能用。

题 2：
- 不打印秒数，是因为同一次循环，每次跑的秒数都会浮动。谁更慢，看名字就够了。
- cProfile 只记下 enable 和 disable 之间、这次进程里的调用。
  一个已经在跑的进程，你没有在它下面重新启动，这段记录里就没有它。
  那种情况从外面看栈，用 py-spy。本课不安装它。
"""

from __future__ import annotations

import cProfile
import pstats


def bread() -> int:
    return 1


def milk() -> int:
    total = 0
    for i in range(200_000):
        total = total + i
    return total


def hottest(names: set[str]) -> str:
    profile = cProfile.Profile()
    profile.enable()
    bread()
    milk()
    profile.disable()
    best_name = ""
    best_time = -1.0
    for (_filename, _line, name), (_cc, _nc, tottime, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name in names and tottime > best_time:
            best_name = name
            best_time = tottime
    return best_name


def main() -> None:
    print("最慢", hottest({"bread", "milk"}))


if __name__ == "__main__":
    main()
