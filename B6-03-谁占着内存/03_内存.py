"""选修 B6 第 3 课：慢和占内存不是同一件事。tracemalloc 看谁分配的。

对照堆转储。这里不把整个堆倒出来，只看从 start 之后多出来的字节。
["买牛奶"] * 100000 是十万个指针指着同一个字符串，不是十万份文字。
64 位上一个指针 8 字节，所以是 800000。删掉并回收之后，这段不该继续占着。
"""

from __future__ import annotations

import gc
import tracemalloc

COUNT = 100_000


def main() -> None:
    tracemalloc.start()  # 从这里开始记分配。之前的对象不在这组数里。
    # 当前占着多少，以及到现在的峰值。峰值这课不用。
    before, _peak = tracemalloc.get_traced_memory()
    data = ["买牛奶"] * COUNT  # 列表有十万个槽。字符串只有一份。
    held, _peak = tracemalloc.get_traced_memory()
    print("占着", held - before)
    del data  # 名字没了。没有循环引用时，引用计数会马上把列表收回。
    gc.collect()  # 有循环引用时才靠它。这里调用一次，避免漏掉那种情况。
    freed, _peak = tracemalloc.get_traced_memory()
    if freed < held:
        print("已释放")
    else:
        print("还在")
    tracemalloc.stop()


if __name__ == "__main__":
    main()
