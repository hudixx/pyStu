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
    best_time = -1
    for key, value in pstats.Stats(profile).stats.items():
        if key[2] in names and value[2] > best_time:
            best_time = value[2]
            best_name = key[2]
    return best_name

def main() -> None:
    print("最慢", hottest({"bread", "milk"}))

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出