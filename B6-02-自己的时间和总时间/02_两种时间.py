"""选修 B6 第 2 课：自身时间不含叫出去的函数。总时间含。

outer 几乎只是去调用 inner。它的自身时间很短，总时间把 inner 算进来，所以更长。
inner 自己做循环，没有再往下叫，自身时间和总时间分不开。

对照看一份剖析报告：父函数的总时间大，不代表该改父函数。
py-spy 是另一件工具。进程已经在跑、不能重启时，从外面采样看它的栈。
本课不安装 py-spy。Windows 上它经常要管理员权限。练习仍用 cProfile。
"""

from __future__ import annotations

import cProfile  # 剖析器。enable 到 disable 之间的函数调用都会被记下来。
import pstats  # 把记录整理成字典，才能按函数名取出两种时间。


def inner() -> int:
    """时间花在这里。它不再调用别的函数。

    逻辑：把 0 到 199999 加起来返回。没有再调用别人，所以自身时间和总时间应分不开。
    """

    total = 0
    for i in range(200_000):
        # range 产生 0 到 199999。200_000 的下划线只方便读，值是二十万。
        total += i  # total = total + i。整数不可变，每次是一个新的整数贴回这个名字。
    return total


def outer() -> int:
    """自己几乎不干活，只把 inner 叫起来。

    逻辑：把 inner 的返回值原样交回去。outer 的自身时间只是「调用」这一下，总时间包含 inner 的循环。
    """

    return inner()  # 先跑完 inner，再把它的结果当作 outer 的结果。对照 return inner();


def relation(tottime: float, cumtime: float) -> str:
    """总时间明显大于自身时间，就说明时间在它叫出去的函数里。

    逻辑：
    - cumtime 比 tottime 大出超过 1e-9，返回「自身小于总时间」。这是 outer 的情况。
    - 否则返回「自身等于总时间」。inner 没有下属，两种时间应贴在一起。
    不用 == 比浮点。两次测量的误差会让「本来一样」差出极小的一截。
    """

    if cumtime > tottime + 1e-9:  # 浮点不要用 ==。差一点点不算「大于」。
        # 1e-9 是科学计数法，即 0.000000001。对照 1e-9。加在自身时间上，当一条「算明显更大」的缝。
        return "自身小于总时间"
    return "自身等于总时间"


def report() -> dict[str, str]:
    """剖析一次 outer()，记下 outer 和 inner 各自的两种时间。

    逻辑：
    1. 只在 outer() 这一次调用周围开剖析。
    2. 遍历报告。名字是 outer 或 inner 时，把 relation 的那句结论放进字典。
    3. 返回这张字典。键是函数名，值是那句中文，不是秒数。
    """

    profile = cProfile.Profile()
    profile.enable()
    outer()  # 这一次会连带叫起 inner。两条都会出现在报告里。
    profile.disable()
    found: dict[str, str] = {}  # 空字典。对照 new HashMap<String, String>()。冒号是类型标注，不是在造数据。
    # 键是 (文件, 行号, 函数名)。值的第三、第四个是自身时间 tottime、总时间 cumtime。
    # items() 一次给出键和值。左边两层圆括号是在拆包，不是在调用函数。
    for (_filename, _line, name), (_cc, _nc, tottime, cumtime, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name in {"outer", "inner"}:
            # {"outer", "inner"} 是集合。in 问名字在不在里面。对照 Set.of(...).contains(name)。
            found[name] = relation(tottime, cumtime)  # 方括号赋值：没有这个键就新增。对照 map.put。
    return found


def main() -> None:
    """打印 outer 和 inner 各自的结论。预期 outer 是「自身小于总时间」，inner 是「自身等于总时间」。

    found["outer"] 键不存在会抛 KeyError。这一课的报告里两个名字都应在。
    """

    found = report()
    print("outer", found["outer"])
    print("inner", found["inner"])


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 自身时间不含它叫出去的函数，总时间含。outer 的总时间大，是因为 inner 在干活，不该先去改 outer。
# inner 没有再往下叫，两种时间分不开。
# 浮点不要用 == 判断「相等」。差超过 1e-9 才算总时间明显更大。
