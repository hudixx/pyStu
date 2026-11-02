from __future__ import annotations

import cProfile
import pstats

def fill() -> None:
    total = 0
    for i in range(200000):
        total += i

def pack() -> None:
    fill()

def relation(total: float,all_total: float) -> str:
    return  "自身小于总时间" if all_total > total + 1e-9 else "自身等于总时间"

def report() -> dict[str, str]:
    profile = cProfile.Profile()
    profile.enable()
    pack()
    profile.disable()
    found: dict[str, str] = {}
    for (_filename, _line, name), (_cc, _nc, tottime, cumtime, _callers) \
            in pstats.Stats(profile).stats.items():
        found[name] = relation(tottime, cumtime)
    return found

def main() -> None:
    found = report()
    print("pack", found["pack"])
    print("fill", found["fill"])

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出