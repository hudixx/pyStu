# 推迟注解求值。下面的 -> bool、-> int 在 import 时不会被执行。解释器默认也不按这些标注拦错。
from __future__ import annotations

class OrderId:
    # 没有写文档字符串。类体从 __init__ 开始。对照一个只有字段和 equals/hashCode 的类。

    def __init__(self, value: str) -> None:
        # __init__ 是构造器。写 OrderId("A-1") 时解释器调用它。self 就是 this，调用时不要自己传。
        # value: str 只是标注。运行时传一个整数进来，这一行也不会拦，除非另外跑 mypy。
        self.value = value  # 在这个对象上建字段 value。不用事先声明。对照 this.value = value。

    def __eq__(self, other: object) -> bool:
        # 你写 order1 == order2 时，解释器调用 order1.__eq__(order2)。不要自己点 __eq__。
        # other 标成 object：对方可能不是 OrderId，不能一上来就点 other.value。
        if not isinstance(other, OrderId):
            # isinstance(对象, 类) 对照 instanceof。子类也算这一种。
            # NotImplemented 是一个值，不是异常。意思是「我不会比，请试另一边的 __eq__」。
            # 不要写成 return False，也不要写成 raise NotImplementedError（那是「子类还没实现」的异常）。
            return NotImplemented
        return self.value == other.value  # 字符串 == 看内容。对照 equals，不是比两个引用是不是同一个。

    def __hash__(self) -> int:
        # 放进 set、以及用 in 查找时，解释器会调用 __hash__。对照 hashCode。
        # hash(...) 是内置函数，把一个对象变成整数。这里必须用和 __eq__ 相同的字段，也就是 value。
        # 同一次运行里，同一个字符串的 hash 不变。解释器重新启动后这个整数会变，所以不能存进数据库。
        return hash(self.value)


def main() -> None:
    order1 = OrderId("A-1")  # 调用 __init__。order1 这个名字贴在新对象上。对照 OrderId order1 = new OrderId("A-1")。
    order2 = OrderId("A-1")  # 又 new 了一个。值相同，但是另一个对象。
    print("相等:", order1 == order2)  # == 进 __eq__。两个 value 都是 "A-1"，所以是 True。
    print("是否为同一个对象:", order1 is order2)  # is 不走 __eq__，只问是不是同一个对象。这里是 False。对照 Java 的 ==。
    set1 = {order1, order2}
    # 花括号加逗号是集合，对照 new HashSet<>() 再 add 两次。值相等时第二个进不去，所以里面只留先放进去的 order1。
    # 空集合要写 set()。写成 {} 得到的是空字典，不是空集合。
    print(len(set1))  # len 是内置函数，问有几个元素。对照 size()。这里应是 1。
    order1.value = "A-2"  # 改的是已经在集合里的那个对象。它的哈希钥匙变了，但集合不会自动重新放桶。
    order2.value = "A-3"  # order2 当初就没留在集合里。改它，不会改到集合里那个对象。

    # iter(set1) 向集合要一个迭代器，对照 iterator()。集合没有下标，不能写 set1[0]。
    # next(...) 是内置函数，取迭代器的下一个，也就是「随便拿出一个」。对照 iterator.next()。
    # 集合只有 1 个元素，拿出来的就是 order1。再点 .value，打印的是它被改过之后的 "A-2"。
    # 集合若是空的，next 会抛 StopIteration。
    print("改过之后set中的元素值：", next(iter(set1)).value)

    # in：按「现在的」__hash__ 去找。value 已经改成 A-2，去的是另一个桶，所以是 False。对照 contains。
    # any(...) 是内置函数：括号里只要有一个为真就返回 True，并且停下。对照 anyMatch。
    # item is order1 for item in seen 这种写法是生成器：逐个拿出元素，问是不是同一个对象。不先做成列表。
    # is 对得上，所以第二个值是 True：人还在集合里，只是按新钥匙找不到。
    print("改过之后", order1 in set1, any(item is order1 for item in set1))


# 直接 python 本文件时才跑 main。被别的文件 import 时，__name__ 不是 "__main__"，下面不执行。
if __name__ == "__main__":
    main()
