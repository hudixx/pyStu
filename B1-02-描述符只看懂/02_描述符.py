"""选修 B1 第 2 课：描述符只看懂。它是属性被点到时跑的代码。

对照：你不会自己写一套 JPA。但要认得「类上的 title 是列，实例上的 title 是值」。
第 50 课的 Todo.title 就是这个机制。property 也是。
"""

from __future__ import annotations


class Positive:
    """把赋值拦下来。小于 0 就拒绝。对照一个只在 setter 里检查的字段。"""

    def __set_name__(self, owner: type, name: str) -> None:
        # 类定义结束时调用一次。name 是类体里的字段名，这里是 balance。
        self.public = name
        self.private = "_" + name  # 真正的数字放在 _balance，避免点 balance 时又进这个描述符。

    def __get__(self, obj: object, objtype: type | None = None) -> object:
        # 用类去点时 obj 是 None。返回描述符自己，所以类上不是那个整数。
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj: object, value: int) -> None:
        if value < 0:
            raise ValueError("不能为负")
        setattr(obj, self.private, value)


class Account:
    """余额走 Positive。类上的 balance 和实例上的 balance 不是同一种东西。"""

    balance = Positive()

    def __init__(self, balance: int) -> None:
        # 这一行会进 Positive.__set__，不是普通的实例字段赋值。
        self.balance = balance


class Ticket:
    """property 是语言写好的描述符。读价格时跑下面的函数。"""

    def __init__(self, price: int) -> None:
        self._price = price

    @property
    def price(self) -> int:
        return self._price


def main() -> None:
    # 类上点到的是描述符对象，不是 100。对照 Todo.title 在类上是列，不是某一行的标题。
    print("类上", type(Account.balance).__name__)
    account = Account(100)
    print("实例", account.balance)
    try:
        Account(-1)
    except ValueError as exc:
        print("拒绝", exc)
    print("property", Ticket(100).price)
    # 类上的 price 是 property 对象。和 Positive 一样，都不是那个整数。
    print("类上的 property", type(Ticket.price).__name__)


if __name__ == "__main__":
    main()
