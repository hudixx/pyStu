"""选修 B5 第 2 课参考答案。题 1 过了。题 2 写在下面。

运行 02_练习.py 看到：

买豆浆 2
买牛奶 1

按题目的顺序加了三次：买豆浆、买牛奶、买豆浆。
读的时候按这个顺序各 get 一次，没有遍历字典。没出现过的标签会是 0，这题没有去读别的标签。

方法里面空行多了一些。本课 ruff 没报，不影响这两个数字。

题 2：
- 每次下单打成一行日志再去数，句子一改，数就断了。日志是用来查某一笔的，不是用来加总的。
  计数器里就是一个数字，现在就能读。
- 用户 id 当标签，每来一个新 id 就多一条序列，条数跟着用户涨。加总也没了意义。
  每一单去日志里查，带上请求号。次数只按要比较的那几类来分，比如标题、成功还是失败。
"""

from __future__ import annotations


class Counter:
    def __init__(self) -> None:
        self._values: dict[str, int] = {}

    def add(self, label: str) -> None:
        current = self._values.get(label, 0)
        self._values[label] = current + 1

    def get(self, label: str) -> int:
        return self._values.get(label, 0)


def main() -> None:
    counter = Counter()
    counter.add("买豆浆")
    counter.add("买牛奶")
    counter.add("买豆浆")
    print("买豆浆", counter.get("买豆浆"))
    print("买牛奶", counter.get("买牛奶"))


if __name__ == "__main__":
    main()
