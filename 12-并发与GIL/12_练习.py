import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor

def timed(fuc, strs: str, list_str: list[str] | None = None) -> None:
    start = time.perf_counter()
    fuc(list_str)
    print(f"{strs}{time.perf_counter() - start:.2f}s")

def wait_one(name: str) -> str:
    time.sleep(0.2)
    return name

def wait_one_thread(list_str: list[str] | None = None) -> None:
    if list_str is None:
        list_str = ["1", "2"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        temps = list(executor.map(wait_one, list_str))
        for temp in temps:
            print(temp)

def wait_one_process(list_str: list[str] | None = None) -> None:
    if list_str is None:
        list_str = ["1", "2"]
    with ProcessPoolExecutor(max_workers=4) as executor:
        temps = list(executor.map(wait_one, list_str))
        for temp in temps:
            print(temp)
def main() -> None:
    print_list = ["a", "b", "c", "d"]
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        temps = list(executor.map(wait_one, print_list))
        for temp in temps:
            print(temp)
    print(f"线程方式用时: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    for temp in print_list:
        print(wait_one(temp))
    print(f"串行用时: {time.perf_counter() - start:.2f}s")

    timed(wait_one_thread,"线程方式用时: ", print_list )
    timed(wait_one_process, "进程方式用时: ", print_list )

    timed(wait_one_thread,"线程方式用时: " )
    timed(wait_one_process, "进程方式用时: " )


    #第二题
    """
    线程池做 CPU，有没有接近「变成 1/4 时间」？
        没有
    为什么？（一句话，提到 GIL）
        纯 Python 的 进行cpu密级时 几乎不释放 GIL，线程几乎不加速， 四个线程 ≈ 一个线程的时间，还可能更慢（抢锁）
    若进程池反而更慢，是不是说明 GIL 不存在？
        不是。任务轻时进程启动更贵
    """
    #第三题
    """
    Java 里 CPU 密集任务丢线程池常常能吃多核。同样的直觉为什么不能直接搬到 CPython？ 什么时候你应该改用 ProcessPoolExecutor？
        不知道,请给我答案,要简洁明要
        CPython 同一时刻只有一个线程在执行 Python 字节码（GIL）。Java 线程能把多核算力叠上去；CPython 线程叠不上 CPU
        改用 ProcessPoolExecutor 的时机： 瓶颈是纯 Python / 算得凶的 CPU，不是在等 IO。每个进程有自己的解释器和一份 GIL，才能真吃多核。代价是启动贵、数据要能序列化、内存不共享。
    """
    #第四题
    """
    为什么本课示例的进程池要放在 if __name__ == "__main__": 里？
        不知道,请给我答案,要简洁明要
        Windows 用 spawn 起子进程：子进程会 重新 import 本文件。若进程池写在模块顶层，import 时又创建进程池 → 再 import → 无限套娃。
    """

if __name__ == "__main__":
    main()