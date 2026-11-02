"""选修 B6 第 1 课：先量出谁最慢，再改。不要凭感觉挑函数。

对照 JFR。cProfile 把程序跑在它下面，每个函数花了多少自身时间都能对上。
本课只打印函数名，不打印秒数。秒数每次会浮动，名字不会。
"""

# 推迟注解求值。set[str] 这种写法在 import 时不会被执行。
from __future__ import annotations

import cProfile  # 标准库的剖析器。对照 JFR：把这段代码跑一遍，记下每个函数花了多久。
import pstats  # 把 cProfile 记下来的原始数据整理成能遍历的表。对照读一份剖析报告。


def fast() -> int:
    """几乎不干活。用来对照。

    逻辑：直接返回 1。没有循环，自身时间应远小于 slow。
    -> int 对照返回 int。解释器不检查。
    """

    return 1  # return 把值交回调用方。这里的 1 没人接住，调用方只要它跑过。


def slow() -> int:
    """把一段循环跑完。这段才是时间花掉的地方。

    逻辑：从 0 加到 199999，把总和返回。时间花在这二十万次加法上。
    """

    total = 0  # 整数。+= 会换成一个新的整数再贴回这个名字，不是改原来那个对象的内部。
    for i in range(200_000):  # 下划线只方便读，值还是二十万。
        # range(n) 产生 0, 1, ..., n-1。对照 for (int i = 0; i < 200_000; i++)。
        # 200_000 里的下划线是数字分隔符，解释器不当成运算。对照 Java 的 200_000。写成 200000 是同一个数。
        total += i  # 等价于 total = total + i。
    return total


def hottest(names: set[str]) -> str:
    """在这几个名字里，找出自身时间最长的那个。

    逻辑：
    1. 打开剖析，只包住 fast() 和 slow() 这两次调用。定义函数的时间不算。
    2. 关掉剖析，遍历每个函数的自身时间。
    3. 名字在 names 里、并且自身时间更大，就记下这个名字。
    4. 返回名字，不返回秒数。秒数每次跑都会浮动。
    names 是集合。对照 Set<String>。in 问这个名字在不在里面。
    """

    profile = cProfile.Profile()  # 造一个空的记录器。这时还没开始记。
    profile.enable()  # 从这里开始记。之前定义函数的时间不算。
    fast()  # 调用。返回值丢掉。剖析器会看见这次调用。
    slow()
    profile.disable()  # 停止记录。后面遍历报告的时间不要算进 slow。
    best_name = ""  # 还没找到时的占位。若 names 里一个都没出现在报告里，就返回这个空串。
    best_time = -1.0  # 用负数当「还没见过」。自身时间不会是负数，所以第一个候选一定比它大。
    # stats 的键是 (文件, 行号, 函数名)。值是五元组：
    # 原始调用次数、总调用次数、自身时间、总时间、谁调用了它。
    # .stats 是一个字典。items() 一次给出键和值。对照 entrySet。
    # for 左边是两层拆包：键拆成三个，值拆成五个。对照从一个 Pair 里再拆出字段。
    # 下划线开头的名字表示「这份数据我故意不用」。
    for (_filename, _line, name), (_cc, _nc, tottime, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        # name in names：函数名是不是我们关心的那几个。对照 set.contains(name)。
        # tottime 是自身时间，不含它再调出去的函数。这一课 fast 和 slow 都没有再往下叫别人。
        if name in names and tottime > best_time:
            best_name = name
            best_time = tottime  # 记下目前最大的。后面更小的不会再进来。
    return best_name


def main() -> None:
    """只问 fast 和 slow 谁的自身时间更长，把名字打印出来。

    {"fast", "slow"} 是集合字面量。对照 Set.of("fast", "slow")。
    花括号里是逗号分开的元素。没有冒号，所以不是字典。预期打印 slow。
    """

    print("最慢", hottest({"fast", "slow"}))


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 谁最慢要量，不要凭函数名字猜。cProfile 在 enable 和 disable 之间记账。
# 报告里每个函数有自身时间。这一课只比 fast 和 slow，打印名字，不打印秒数，因为秒数每次会浮动。
# range(200_000) 里的下划线只是方便读，值仍是二十万。
