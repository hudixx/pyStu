"""第 12 课参考答案。题 1 的 0.20s vs 0.80s 你已经跑对。

进程池对 sleep 这种 IO 没有优势，启动还更贵（你测到 0.30s）。
IO 用线程，CPU 用进程。
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor


def wait_one(name: str) -> str:
    time.sleep(0.2)
    return name


def main() -> None:
    names = ["a", "b", "c", "d"]

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(wait_one, names))
    print(results)
    print(f"线程池: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    serial = [wait_one(name) for name in names]
    print(serial)
    print(f"串行: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
