from __future__ import  annotations

import cProfile
import pstats
import importlib
import sys

def calls_of_build() -> int:
    profile = cProfile.Profile()
    profile.enable()
    importlib.import_module("costly")
    profile.disable()
    for (_filename, _line, name), (_cc, ncalls, _tt, _ct, _callers) in pstats.Stats(
        profile
    ).stats.items():
        if name == 'heat':
            return ncalls
    return 0

def main() -> None:
    sys.modules.pop("costly", None)
    print("第一次导入", "heat", calls_of_build())
    print("第二次导入", "heat", calls_of_build())

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出