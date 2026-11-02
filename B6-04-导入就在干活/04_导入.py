"""选修 B6 第 4 课：import 会执行模块体。第一次付出代价，同进程里的第二次不会。

对照静态初始化块。类加载时跑的代码，每次新进程都要再付一次。
同一次进程里第二次 import 直接拿到 sys.modules 里的那份，build 不会再被调用。
所以「再 import 一次很快」不能说明启动不慢。慢的是每个新进程的第一次。
"""

from __future__ import annotations

import cProfile
import importlib
import pstats
import sys


def calls_of_build() -> int:
    """只剖析这一次 import。返回剖析结果里 build 被调用了几次。"""

    profile = cProfile.Profile()
    profile.enable()
    importlib.import_module("heavy")  # 同目录下的 heavy.py。脚本目录会在 sys.path 的前面。
    profile.disable()
    for (_filename, _line, name), (_cc, ncalls, _tt, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name == "build":
            return ncalls
    return 0  # 这次 import 没有执行 build。第二次就是这样。


def main() -> None:
    sys.modules.pop("heavy", None)  # 保证这一次是第一次，不受之前残留的模块影响。
    print("第一次导入", "build", calls_of_build())
    # 不要再 pop。留下缓存，第二次应是 0。
    print("第二次导入", "build", calls_of_build())


if __name__ == "__main__":
    main()
