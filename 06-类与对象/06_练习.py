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
        return self._owner



class Bag:
    items = []

    def add(self, x: str) -> None:
        self.items.append(x)

class SafeBag:
    def __init__(self) -> None:
        self.items = []
    def add(self, x: str) -> None:
        self.items.append(x)




def main() -> None:
    # 第一题
    ac = Account("hudi", 100)
    ac.deposit(50)
    print(ac.summary())
    # 第二题
    a = Bag()
    b = Bag()
    a.add("java")
    print(b.items) # 打印 java . 因为 items 是可变量 且 items = [] 写在class体里是类属性，使用 = [] 的方式，是公用一份。

    a = SafeBag()
    b = SafeBag()
    a.add("java")
    print(b.items)

    # 第三题
    print(ac.owner)
    try:
        ac.owner = "ada"
    except AttributeError as exc:
        print(exc)

    #第四题    因为Python自动吧自己传进第一个参数，所以方法必须写self



if __name__ == "__main__":
    main()