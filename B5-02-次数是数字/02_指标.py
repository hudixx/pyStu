"""选修 B5 第 2 课：要加总的次数是一个数字，不是从日志里数句子。

对照 Micrometer 的 Counter。标签是用来分组的，不是用来记下每一单。
用户 id、订单号当标签，每来一个新 id 就多一条永远涨的序列。
本课自己写一个计数器，把「加一」和「读出数字」露出来。
生产换成 prometheus_client 的 Counter，调用形状一样。
那个库的注册表是全局的，同名再建一次会抛。这里不装它。
"""

from __future__ import annotations


class Counter:
    """按标签分开加总。没出现过的标签，读出来是 0，不是抛错。"""

    def __init__(self) -> None:
        self._values: dict[str, int] = {}  # 标签到次数。下划线开头表示给类自己用。

    def add(self, label: str) -> None:
        """这个标签加 1。没有就从 0 开始。"""

        current = self._values.get(label, 0)  # 没有这个键时用 0。对照 map.getOrDefault。
        self._values[label] = current + 1

    def get(self, label: str) -> int:
        """读现在的次数。没加过就是 0。"""

        return self._values.get(label, 0)


def main() -> None:
    counter = Counter()
    counter.add("买牛奶")
    counter.add("买牛奶")
    counter.add("买面包")
    # 按我们要的顺序读。不要遍历字典，插入顺序和你想打印的顺序不一定一样。
    print("买牛奶", counter.get("买牛奶"))
    print("买面包", counter.get("买面包"))


if __name__ == "__main__":
    main()
