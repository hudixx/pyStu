"""选修 B1 第 1 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来应是：
相等 True
个数 1
改过之后 False True

练习里 __eq__ 和 __hash__ 都用了 value。两个 OrderId("A-1") 相等，set 里只有 1 个。
改掉参与哈希的字段之后，in 是 False，遍历仍能碰到原来那个对象。这是对的。

打印多了几行，不影响这三件事实：
- 「相等:」带了冒号。题目要的是「相等 True」。
- 多印了 is，结果是 False。两个对象值相同，但不是同一个。这是对的。
- 个数印成了单独一个 1，没有「个数」这两个字。
- 两个对象都放进了 set，又把第二个的 value 改成了 A-3。
  值相同的时候，set 留下先放进去的那个，第二个根本不在里面。
  所以集合里印出来的 A-2，是第一个对象被改过之后的值，不是改第二个改出来的。

题 3：
- 只写 __eq__、不写 __hash__，Python 3 会把 __hash__ 设成 None。
  放进 set 时要先算哈希，于是直接 TypeError，不会装进去。
  Java 不会因为你写了 equals 就把 hashCode 清掉。默认的 hashCode 仍按对象身份算。
  于是 HashSet 能装进两份值相同的对象，之后按值又找不到。Python 是直接拒绝，不让这个错悄悄发生。
- list 不能拿去算哈希。hash(某个 list) 会 TypeError，它也不能当字典的键。
  就算能算，list 以后还能改。哈希依赖会变的东西，set 就会找不到它。
  这和本课把 value 改成 A-2 是同一类错。参与 __eq__ 和 __hash__ 的字段放进集合之后不能改。
"""

from __future__ import annotations


class OrderId:
    """订单号按值相等。value 放进 set 之后不要再改。"""

    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        # 类型不对就交给对方试。不要直接 return False。
        if not isinstance(other, OrderId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        # 和 __eq__ 用同一个字段。对照 hashCode 必须和 equals 用同一组字段。
        return hash(self.value)


def main() -> None:
    one = OrderId("A-1")
    two = OrderId("A-1")
    print("相等", one == two)  # True。看的是值，不是是不是同一个对象。
    print("个数", len({one, two}))  # 1。第二个因相等而进不去。

    seen = {one}
    one.value = "A-2"  # 放进去之后改了参与哈希的字段。
    # in 按现在的哈希去找，找不到。遍历仍能碰到原来那个对象。
    print("改过之后", one in seen, any(item is one for item in seen))


if __name__ == "__main__":
    main()
