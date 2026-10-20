"""选修 B1 第 1 课：相等看值，哈希和相等必须一起写。

对照 Java 的 equals 和 hashCode。
Java 里只改 equals、不改 hashCode，HashSet 会装进两份，而且找不回来。
Python 更严：写了 __eq__ 却不写 __hash__，放进 set 会直接 TypeError。
"""

from __future__ import annotations


class Bare:
    """没写相等，也没写哈希。对照一个没改 equals 的类：比的是不是同一个对象。"""

    def __init__(self, code: str) -> None:
        self.code = code


class OnlyEq:
    """只写了相等。Python 会把 __hash__ 设成 None，这个对象不能放进 set。"""

    def __init__(self, code: str) -> None:
        self.code = code

    def __eq__(self, other: object) -> bool:
        # 不是同一种类型，交给对方试。不要直接 return False，否则两边的结果会不对称。
        if not isinstance(other, OnlyEq):
            return NotImplemented
        return self.code == other.code


class Sku:
    """值和哈希一起写。参与哈希的字段之后不能改，否则 set 会找不到它。"""

    def __init__(self, code: str) -> None:
        self.code = code

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sku):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        # 和 __eq__ 用同一份字段。对照 hashCode 必须和 equals 用同一组字段。
        return hash(self.code)


def main() -> None:
    left = Bare("SKU-8891")
    right = Bare("SKU-8891")
    # == 是 False：默认比的是不是同一个对象，对照 == 在没改 equals 时比引用。
    # 两个都能进 set：默认哈希也按对象身份，所以个数是 2。
    print("没写相等", left == right, len({left, right}))

    try:
        # 构造 set 时就要算哈希。只有相等、没有哈希，这里抛 TypeError。
        {OnlyEq("SKU-8891")}
    except TypeError:
        print("只写相等 TypeError")

    one = Sku("SKU-8891")
    two = Sku("SKU-8891")
    # == 是 True，is 是 False。两个对象值相同，但不是同一个。set 里只留 1 个。
    print("写全了", one == two, one is two, len({one, two}))

    seen = {one}
    one.code = "SKU-0000"  # 放进 set 之后又改了参与哈希的字段。对照改了已经在 HashSet 里的键。
    # in 按现在的哈希去找，找不到。遍历仍能碰到原来那个对象，它还在桶里，只是钥匙变了。
    print("改过之后", one in seen, any(item is one for item in seen))


if __name__ == "__main__":
    main()
