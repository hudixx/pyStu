from __future__ import annotations

print("进入引用")
def heat() -> int:

    print("进入heat")
    total = 0
    for i in range(100_000):
        total += i
    return total


heat = heat()