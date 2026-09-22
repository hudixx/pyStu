"""第 12 课示例：线程适合 IO，进程适合 CPU。

对照 Java ExecutorService。Windows 上进程池必须放在 main 里启动。
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def pretend_io(n: int) -> int:
    """模拟 IO：sleep 会释放 GIL，多线程能重叠等待。"""
    time.sleep(0.3)
    return n


def pretend_cpu(n: int) -> int:
    """模拟 CPU：纯 Python 循环，线程加速不了。"""
    total = 0
    # 太小的话，进程启动开销会盖过计算时间，看起来进程反而更慢
    for i in range(8_000_000):
        total += i % (n + 1)
    return total


def timed(label: str, func) -> None:
    start = time.perf_counter()
    func()
    print(f"{label}: {time.perf_counter() - start:.2f}s")


def run_io_serial() -> None:
    for i in range(4):
        pretend_io(i)


def run_io_threads() -> None:
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(pretend_io, range(4)))

def run_io_processes() -> None:
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(pretend_io, range(4)))

def run_cpu_threads() -> None:
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(pretend_cpu, range(4)))


def run_cpu_processes() -> None:
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(pretend_cpu, range(4)))


def main() -> None:
    print("=== IO（sleep）：串行 vs 线程 ===")
    timed("串行 4×0.3s", run_io_serial)       # 大约 1.2s
    timed("线程池 4 个", run_io_threads)        # 大约 0.3s
    timed("进程池 4 个", run_io_processes)        # 大约 0.3s

    print("=== CPU：线程 vs 进程（看谁更快）===")
    timed("线程池做 CPU", run_cpu_threads)
    timed("进程池做 CPU", run_cpu_processes)


if __name__ == "__main__":
    main()
