from __future__ import annotations


import gc
import tracemalloc


COUNT = 100_000


def main() -> None:
    tracemalloc.start()
    before, _peak = tracemalloc.get_traced_memory()
    data = ["买豆浆"] * COUNT
    held, _peak = tracemalloc.get_traced_memory()
    print("占着", held - before)
    del data
    gc.collect()
    freed, _peak = tracemalloc.get_traced_memory()
    if freed < held:
        print("已释放")
    else:
        print("还在")
    tracemalloc.stop()

if __name__ == "__main__":
    main()
#  题2不知道，请在参考答案的注释中个给出