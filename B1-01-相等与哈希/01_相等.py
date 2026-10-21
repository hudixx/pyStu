"""选修 B1 第 1 课：相等看值，哈希和相等必须一起写。

对照 Java 的 equals 和 hashCode。
Java 里只改 equals、不改 hashCode，HashSet 会装进两份，而且找不回来。
Python 更严：写了 __eq__ 却不写 __hash__，放进 set 会直接 TypeError。
"""

# 推迟注解求值。-> bool 这类标注在 import 时不会被执行。删掉也能跑，主要给人和 mypy 看。
from __future__ import annotations


class Bare:
    """没写相等，也没写哈希。对照一个没改 equals 的类：比的是不是同一个对象。"""

    def __init__(self, code: str) -> None:
        # __init__ 是构造器，两边各两个下划线。你写 Bare("SKU-8891") 时，解释器会来调它。
        # 不要自己写 obj.__init__(...)。对照 Java 的构造方法，但第一个参数 self 就是 this，调用时不用传。
        # code: str 是参数类型，-> None 表示没有返回值（对照 void）。解释器默认不检查这些标注。
        self.code = code  # 在对象上建一个字段。Python 不用先声明字段。对照 this.code = code。


class OnlyEq:
    """只写了相等。Python 会把 __hash__ 设成 None，这个对象不能放进 set。"""

    def __init__(self, code: str) -> None:
        self.code = code  # 同上。这是实例字段，每个对象各有一份。

    def __eq__(self, other: object) -> bool:
        # __eq__ 就是 equals。你写 left == right 时，解释器调用 left.__eq__(right)，不是你自己点这个名字。
        # other: object 对照参数类型是 Object：对方可能是任何对象，不能假设它也有 .code。
        # 不是同一种类型，交给对方试。不要直接 return False，否则两边的结果会不对称。
        if not isinstance(other, OnlyEq):
            # isinstance(对象, 类) 对照 other instanceof OnlyEq。父类、子类都算。不是 == 类型名字。
            # NotImplemented 是一个现成的单例值，不是异常，也不是 NotImplementedError。
            # 把它 return 出去，意思是「我不会比，请用另一边的 __eq__ 再试一次」。
            # 两边都不会比，Python 才退回到「是不是同一个对象」。
            return NotImplemented
        return self.code == other.code  # 字符串的 == 看内容。对照 String.equals，不是比两个引用。


class Sku:
    """值和哈希一起写。参与哈希的字段之后不能改，否则 set 会找不到它。"""

    def __init__(self, code: str) -> None:
        self.code = code

    def __eq__(self, other: object) -> bool:
        # 和 OnlyEq 同一套。== 会进这里。类型不对就返回 NotImplemented，不要返回 False。
        if not isinstance(other, Sku):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        # __hash__ 就是 hashCode。放进 set、用 in 查找时，解释器会调用它，你不要自己点这个名字。
        # 和 __eq__ 用同一份字段。对照 hashCode 必须和 equals 用同一组字段。
        # hash(...) 是内置函数：给一个对象算整数。字符串的 hash 每次启动解释器都会变（防攻击加了盐），
        # 但同一次运行里，同一个字符串算出的整数不变。所以能当这次进程里的 set 钥匙，不能存进数据库下次再用。
        return hash(self.code)


def main() -> None:
    left = Bare("SKU-8891")  # 调用 Bare.__init__。left 这个名字贴在新对象上。对照 Bare left = new Bare(...)。
    right = Bare("SKU-8891")  # 另一个对象。内容一样，但是另一个。对照又 new 了一次。
    # == 是 False：默认比的是不是同一个对象，对照 == 在没改 equals 时比引用。
    # 两个都能进 set：默认哈希也按对象身份，所以个数是 2。
    # {left, right} 是集合字面量，对照 new HashSet<>() 再 add 两次。花括号里是逗号分开的元素。
    # 不要和字典搞混：字典是 {键: 值}。空集合必须写 set()，写成 {} 得到的是空字典。
    # len(...) 是内置函数，问「里面有几个」。对照 size()。
    print("没写相等", left == right, len({left, right}))

    try:
        # 构造 set 时就要算哈希。只有相等、没有哈希，这里抛 TypeError。
        # {OnlyEq(...)} 只有一个元素，仍然要算哈希才能决定放进哪个桶。对照 new HashSet 再 add。
        {OnlyEq("SKU-8891")}
    except TypeError:
        # TypeError 是类型用错了，比如把不能哈希的对象放进 set。对照 ClassCastException 那一类，不是业务异常。
        # 这里不写 as：不需要异常对象本身，只要知道是这一种。
        print("只写相等 TypeError")

    one = Sku("SKU-8891")
    two = Sku("SKU-8891")
    # == 是 True，is 是 False。两个对象值相同，但不是同一个。set 里只留 1 个。
    # is 比的是「是不是同一个对象」，对照 Java 的 ==。它不走 __eq__。
    # 和 None 比较时要写 x is None，不要写 x == None。None 是唯一的空对象。
    print("写全了", one == two, one is two, len({one, two}))

    seen = {one}  # 集合里现在有 one。钥匙是当时的 hash("SKU-8891")。
    one.code = "SKU-0000"  # 放进 set 之后又改了参与哈希的字段。对照改了已经在 HashSet 里的键。
    # in 是「在不在里面」。对 set，先用现在的 __hash__ 找桶，再在桶里用 __eq__ 比。
    # 对照 set.contains(one)。哈希变了，就去错的桶里找，所以是 False。
    # any(...) 是内置函数：有一个为真就返回 True，并且不再往下看。对照 stream.anyMatch。
    # 圆括号里是生成器：item is one for item in seen。意思是「逐个拿出元素，检查是不是同一个对象」。
    # 它不先做成列表。对照 for (Item item : seen) { if (item == one) return true; }，这里用的是 is，不是 ==。
    print("改过之后", one in seen, any(item is one for item in seen))


# 直接 python 本文件时 __name__ 才是 "__main__"。被 import 时下面不执行。
# 对照类里的 main 不会因为别人引用了这个类就自动跑。
if __name__ == "__main__":
    main()
