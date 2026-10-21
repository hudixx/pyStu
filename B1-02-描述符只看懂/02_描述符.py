"""选修 B1 第 2 课：描述符只看懂。它是属性被点到时跑的代码。

对照：你不会自己写一套 JPA。但要认得「类上的 title 是列，实例上的 title 是值」。
第 50 课的 Todo.title 就是这个机制。property 也是。

两边带双下划线的方法（__init__、__get__、__set__）都是解释器在特定时机自己调用的。
你写 account.balance 或 account.balance = 100，不要自己写 account.__get__(...)。
"""

from __future__ import annotations


class Positive:
    """把赋值拦下来。小于 0 就拒绝。对照一个只在 setter 里检查的字段。"""

    def __set_name__(self, owner: type, name: str) -> None:
        # 类定义结束时调用一次，不是每次 new 都调。Account 写完时，解释器对 balance = Positive() 调这个方法。
        # owner 是拥有它的类，这里是 Account。name 是类体里的字段名，这里是 "balance"。对照注解处理器看见字段名。
        # 类上的 title 是列，实例上的 title 是值。这个方法只负责记住名字。
        self.public = name  # 公开的名字，本课后面没用它。留着是为了看清「描述符知道自己叫什么」。
        self.private = "_" + name  # 字符串拼接。得到 "_balance"。真正的数字放这里。
        # 为什么不直接放在 balance 上：点 balance 会再进这个描述符，自己调用自己，堆栈会爆。

    def __get__(self, obj: object, objtype: type | None = None) -> object:
        # 读属性时调用。account.balance 会进这里，obj 是那个 account。
        # 用类去点时（Account.balance）obj 是 None。objtype 是类本身。= None 是默认值，调用时可以不传。
        # type | None 对照 @Nullable Class。
        if obj is None:
            # is 问是不是同一个对象。和 None 比较用 is，不用 ==。
            # 返回描述符自己，所以类上不是那个整数。print 时看到的是 Positive 这个对象。
            return self
        # getattr(对象, 名字) 是内置函数：按字符串取出属性。对照反射 Field.get。
        # getattr(obj, "_balance") 就是 obj._balance，但名字存在变量里，不能写成 obj.self.private。
        return getattr(obj, self.private)

    def __set__(self, obj: object, value: int) -> None:
        # 赋值时调用。self.balance = 100 进这里，value 是 100。没有 __set__ 的描述符是只读的。
        if value < 0:
            raise ValueError("不能为负")  # raise 对照 throw。构造器里的赋值也会进这里，所以 Account(-1) 会失败。
        # setattr(对象, 名字, 值) 是内置函数，和 getattr 一对。对照反射 Field.set。
        # 写到 _balance 上，不会再进 __set__。如果 setattr(obj, "balance", value)，会无限递归。
        setattr(obj, self.private, value)


class Account:
    """余额走 Positive。类上的 balance 和实例上的 balance 不是同一种东西。"""

    # 这一行在类体里执行一次，造一个 Positive，放在类上。不是每个实例各造一个。
    # 对照 static 字段上挂了一个拦截器。第 50 课的 title = mapped_column(...) 也是这种「类上放一个描述符」。
    balance = Positive()

    def __init__(self, balance: int) -> None:
        # 这一行会进 Positive.__set__，不是普通的实例字段赋值。
        # 参数名也叫 balance，和属性重名。右边的 balance 是参数，左边的 self.balance 才走描述符。
        self.balance = balance


class Ticket:
    """property 是语言写好的描述符。读价格时跑下面的函数。"""

    def __init__(self, price: int) -> None:
        # 下划线开头是约定：请别从外面点 _price。语言不阻止你点。对照包内可见，不是 private。
        self._price = price  # 普通赋值。这个名字上没有描述符，所以不会进 __set__。

    @property
    def price(self) -> int:
        # @property 是装饰器：把这个方法收成一个描述符，挂在类上。对照 getter，但外面写 ticket.price，不写 getPrice()。
        # 没有写 setter，所以 Ticket 造好后不能 ticket.price = 1，会抛 AttributeError。
        return self._price  # 读的是上面存好的普通字段。


def main() -> None:
    # type(某个对象) 是内置函数，问「你是哪个类」。对照 getClass()。
    # __name__ 是类的名字字符串，这里是 "Positive"。对照 getSimpleName()。
    # Account.balance 点的是类，进 __get__ 时 obj 是 None，返回描述符自己，所以 type 得到的是 Positive。
    print("类上", type(Account.balance).__name__)
    account = Account(100)  # __init__ 里的 self.balance = 100 进 __set__，数字放在 _balance。
    print("实例", account.balance)  # 读实例，进 __get__，getattr 取出 100。
    try:
        Account(-1)  # 构造时赋值进 __set__，value < 0，抛 ValueError。对象不会建成功。
    except ValueError as exc:
        # as exc 把异常接住。对照 catch (ValueError e)。print 它会打出「不能为负」。
        print("拒绝", exc)
    print("property", Ticket(100).price)  # 先构造，再读 price。读的时候跑上面那个被 @property 包住的方法。
    # 类上的 price 是 property 对象。和 Positive 一样，都不是那个整数。
    # type(...).__name__ 这里得到 "property"。property 是内置类型的名字。
    print("类上的 property", type(Ticket.price).__name__)


if __name__ == "__main__":
    main()
