"""选修 B5 第 2 课：要加总的次数是一个数字，不是从日志里数句子。

对照 Micrometer 的 Counter。标签是用来分组的，不是用来记下每一单。
用户 id、订单号当标签，每来一个新 id 就多一条永远涨的序列。
本课自己写一个计数器，把「加一」和「读出数字」露出来。
生产换成 prometheus_client 的 Counter，调用形状一样。
那个库的注册表是全局的，同名再建一次会抛。这里不装它。
"""

from __future__ import annotations


class Counter:
    """按标签分开加总。没出现过的标签，读出来是 0，不是抛错。

    一个 Counter 对象里有一张字典：标签到次数。买牛奶和买面包各算各的，不会加到同一个数上。
    """

    def __init__(self) -> None:
        """构造时造一张空字典。没有次数可记，所以不接收参数。

        __init__ 是构造器。写 Counter() 时解释器调用它。self 是 this，调用时不用传。
        """

        self._values: dict[str, int] = {}  # 标签到次数。下划线开头表示给类自己用。
        # dict[str, int] 对照 Map<String, Integer>。= {} 才是空字典。冒号在标注里是「键到值」，不是在造数据。
        # 下划线开头是约定：请别从外面点 _values。语言不阻止。对照包内可见，不是 private。

    def add(self, label: str) -> None:
        """这个标签加 1。没有就从 0 开始。

        逻辑：先取出这个标签现在的次数，没有键就当 0；再把加 1 之后的数写回去。
        不返回新的总数。要看数字，调用 get。
        """

        current = self._values.get(label, 0)  # 没有这个键时用 0。对照 map.getOrDefault。
        # 字典的 get 和 cache.get 不一样：这里第二个参数是默认值。db["title"] 那种方括号写法，键没有会抛 KeyError。
        self._values[label] = current + 1  # 方括号赋值：有这个键就替换，没有就新增。对照 map.put。

    def get(self, label: str) -> int:
        """读现在的次数。没加过就是 0。

        不修改字典。没出现过的标签不会因此被放进 _values。
        """

        return self._values.get(label, 0)  # 再次用默认值。不要写 self._values[label]，没加过会抛 KeyError。


def main() -> None:
    """买牛奶加两次，买面包加一次，再按这个顺序把两个数字打印出来。

    预期：买牛奶 2，买面包 1。读一个从没 add 过的标签会得到 0，本课没有去读。
    """

    counter = Counter()  # 调用 __init__。对照 new Counter()。
    counter.add("买牛奶")
    counter.add("买牛奶")  # 同一个标签再加。字典里还是这一格，值变成 2。
    counter.add("买面包")  # 另一个键。和买牛奶互不影响。
    # 按我们要的顺序读。不要遍历字典，插入顺序和你想打印的顺序不一定一样。
    # for label in counter._values 会按插入顺序走。Python 3.7 起字典记住插入顺序，但打印顺序仍该由你写死。
    # 对照不要靠 HashMap 的迭代顺序当报表顺序。
    print("买牛奶", counter.get("买牛奶"))
    print("买面包", counter.get("买面包"))


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 要加总的次数是一个数字，每次 add 就加 1。不要事后去日志里数有几句「买牛奶」。
# 标签用来分组。每个标签一格。用户 id、订单号当标签，每来一个新 id 就多一格，格数会一直涨。
# 读没加过的标签用 get(键, 0)。用方括号会因为键不存在而抛 KeyError。
