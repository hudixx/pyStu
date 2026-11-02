"""选修 B6 第 4 课：import 会执行模块体。第一次付出代价，同进程里的第二次不会。

对照静态初始化块。类加载时跑的代码，每次新进程都要再付一次。
同一次进程里第二次 import 直接拿到 sys.modules 里的那份，build 不会再被调用。
所以「再 import 一次很快」不能说明启动不慢。慢的是每个新进程的第一次。
"""

from __future__ import annotations

import cProfile  # 只包住这一次 import，才能看见 build 有没有在导入期间被调用。
import importlib  # import_module 按字符串导入。对照 Class.forName，但是导入的是模块，并且会执行模块体。
import pstats  # 从剖析结果里取出 build 的调用次数。
import sys  # sys.modules 是已经导入的模块表。对照类加载器里「这个类已经加载过」的登记处。


def calls_of_build() -> int:
    """只剖析这一次 import。返回剖析结果里 build 被调用了几次。

    逻辑：
    1. enable 之后调用 import_module("heavy")。第一次会执行 heavy.py 的模块体，于是 build 跑一次。
    2. 第二次同名导入不再执行模块体，报告里没有 build，函数返回 0。
    3. 找到名字正好是 build 的那一行，返回它的调用次数。
    """

    profile = cProfile.Profile()
    profile.enable()
    importlib.import_module("heavy")  # 同目录下的 heavy.py。脚本目录会在 sys.path 的前面。
    # import_module("heavy") 对照 import heavy，但名字是字符串，可以写在函数里。
    # 导入时会执行 heavy.py 里不在函数中的那些行。已经在 sys.modules 里则直接返回那份，不再执行。
    profile.disable()
    # 值的第二个数 ncalls 是总调用次数。第一课那行注释里它叫「总调用次数」。
    for (_filename, _line, name), (_cc, ncalls, _tt, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name == "build":
            # == 对字符串比内容。这里要的是函数名正好是 build，不是「名字里含有 build」。
            return ncalls  # 找到就立刻返回。后面的函数不用再看。
    return 0  # 这次 import 没有执行 build。第二次就是这样。


def main() -> None:
    """先清掉可能残留的 heavy，再导入两次，对比 build 的调用次数。

    第一次应是 1。第二次不 pop，缓存还在，应是 0。
    """

    sys.modules.pop("heavy", None)  # 保证这一次是第一次，不受之前残留的模块影响。
    # pop(键, 默认值) 是字典的方法。键在就删掉并返回它的值；键不在就返回 None，不抛 KeyError。
    # 对照 map.remove，但没有这个键时不抛异常。删掉之后，下一次 import 才会重新执行模块体。
    print("第一次导入", "build", calls_of_build())
    # 不要再 pop。留下缓存，第二次应是 0。
    print("第二次导入", "build", calls_of_build())


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# import 会执行模块里不在函数中的代码。heavy.py 末尾那句 built = build() 就在第一次导入时跑完。
# 同一次进程里第二次 import 拿到的是 sys.modules 里的旧模块，build 不会再被调用。
# 所以「再 import 一次很快」不能说明启动不慢。每个新进程的第一次都要再付这笔代价。
