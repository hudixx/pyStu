"""被 04_导入.py 导入。模块体里调用 build，所以第一次 import 就会做完这段循环。"""

from __future__ import annotations


def build() -> int:
    """这段循环不该在 import 时跑。放在函数里，再在模块体调用，第一次导入仍会跑。"""

    total = 0
    for i in range(100_000):
        total += i
    return total


built = build()  # 这一行在 import 时执行。第二次 import 不会再来。
