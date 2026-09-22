"""第 06 课参考答案。四道题你都做对了。

题 2 的机制再精确一点：会共享，不是因为写了 `= []`，
而是因为 `items = []` 写在 **class 体里**（类属性）。
`__init__` 里的 `self.items = []` 同样是 `= []`，却不共享。
"""


class Account:
    def __init__(self, owner: str, balance: int = 0) -> None:
        self._owner = owner
        self.balance = balance

    def deposit(self, amount: int) -> None:
        self.balance += amount

    def summary(self) -> str:
        return f"{self._owner} 的余额是 {self.balance}"

    @property
    def owner(self) -> str:
        """只有 getter，没有 setter → 只读。"""
        return self._owner


class Bag:
    items = []  # 类属性，所有 Bag 实例共享同一张 list

    def add(self, x: str) -> None:
        self.items.append(x)


class SafeBag:
    def __init__(self) -> None:
        self.items = []  # 实例属性，每个对象自己一张表

    def add(self, x: str) -> None:
        self.items.append(x)


def main() -> None:
    ac = Account("hudi", 100)
    ac.deposit(50)
    print(ac.summary())  # hudi 的余额是 150

    a = Bag()
    b = Bag()
    a.add("java")
    print(b.items)  # ['java']

    s1 = SafeBag()
    s2 = SafeBag()
    s1.add("java")
    print(s2.items)  # []

    print(ac.owner)
    try:
        ac.owner = "ada"
    except AttributeError as exc:
        print(exc)


if __name__ == "__main__":
    main()
