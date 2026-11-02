"""选修 B6 第 4 课参考答案。题 1 的次数过了，多打了一行。题 2 写在下面。选修 B6 到这里结束。

运行 04_练习.py 看到：

进入heat
第一次导入 heat 1
第二次导入 heat 0

题目只要后面两行。第一次是 1，第二次是 0。第二次没有再从 sys.modules 里删掉 costly。

heat 里面的 print 多出来了。导入时就会打到控制台。
heat = heat() 把函数名盖成了返回的整数。调用发生在盖住之前，所以剖析仍能数到 1。
导入完成之后，costly.heat 是整数，不再是函数。应写成 built = heat()，把函数留在 heat 上。

from 和 annotations 之间多了一个空格。本课 ruff 没报。

题 2：
- 第二次是 0，是因为同一次进程里模块已经在 sys.modules 里，模块体不会再执行。
  这不能说明循环不慢。每个新进程的第一次导入都要再付这笔。命令行、每个工人、每开一个新的测试进程，都算第一次。
- 只定义 heat、模块体不调用，第一次导入的次数是 0。def 只是把函数造出来，不会跑里面的循环。
"""

from __future__ import annotations

import cProfile
import importlib
import pstats
import sys


def calls_of_heat() -> int:
    profile = cProfile.Profile()
    profile.enable()
    importlib.import_module("costly")
    profile.disable()
    for (_filename, _line, name), (_cc, ncalls, _tt, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name == "heat":
            return ncalls
    return 0


def main() -> None:
    sys.modules.pop("costly", None)
    print("第一次导入", "heat", calls_of_heat())
    print("第二次导入", "heat", calls_of_heat())


if __name__ == "__main__":
    main()
