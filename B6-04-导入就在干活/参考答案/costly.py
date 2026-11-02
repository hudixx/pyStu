"""参考答案里的模块。模块体调用 heat，函数本身还留在 heat 这个名字上。"""

from __future__ import annotations


def heat() -> int:
    total = 0
    for i in range(100_000):
        total += i
    return total


built = heat()
