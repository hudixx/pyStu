"""选修 B6 第 3 课参考答案。题 1 过了。题 2 写在下面。

运行 03_练习.py 看到：

占着 800000
已释放

同一个字符串「买豆浆」重复十万次。64 位上是十万个指针，每个 8 字节。
del 之后再量，当前占用比持有时小，所以是已释放。

顶层函数前面少了一行空行。本课 ruff 没报，不影响这两行。

题 2：
- 十万次「买豆浆」不是十万份文字。列表的每个槽指着同一个字符串。
  涨的是这些指针。8 乘 100000 等于 800000。文字本身只有一份。
- 分配可以很快，字节却留着。时间剖析看不到「还占着」。
  名字还指着这份列表，或者别的地方留着引用，内存就一直在。删掉再量一次，才知道还在不在。
"""

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
