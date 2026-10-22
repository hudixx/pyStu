"""选修 B1 第 2 课参考答案。题 1 过了。题 2 写在下面。

跑出来是：
类上 NonBlank
实例 hudi
拒绝 不能为空

练习里 NonBlank 的 __get__、__set__、__set_name__ 都有。
Person.name 在类上是描述符，实例上是 hudi。空字符串抛了「不能为空」。
没有去写 ORM。

第三行少了「拒绝」两个字。题目要的是「拒绝 不能为空」，练习只 print 了异常本身。
机制是对的，打印少了前缀。

另外两处不影响这次结果：
- obj : object 冒号前面多了一个空格。参数标注写成 obj: object。
- if not value 把空字符串拒绝了，所以这题过了。
  它也会把 None 当成空。题目只要空字符串，写成 value == "" 更贴。

题 2：
- Account.balance 在类上不是 100。
  用类去点时，__get__ 收到的 obj 是 None，描述符返回自己。
  100 是后来赋值时写进实例的 _balance。类上没有那份整数。
  对照第 50 课：Todo.title 在类上是列，某一行上才是这行的标题。
- @property 和 NonBlank 是同一套机制。
  property 是语言写好的描述符。类上点到的是 property 对象，实例上点到才跑那个函数。
  NonBlank 是你自己写的 __get__ 和 __set__。外面都是点一个名字。
- 这一课不让你写 mapped_column。
  只要认出「类上是描述符，实例上是值」。
  mapped_column 还要管表、SQL、会话。自己写会做成半套 ORM，而且做不到那一层。
  看懂即可，不自己做框架。
"""

from __future__ import annotations


class NonBlank:
    """空字符串不让写进去。对照一个在 setter 里拒绝空值的字段。"""

    def __set_name__(self, owner: type, name: str) -> None:
        # 类定义结束时调用一次。name 是类体里的字段名，这里是 "name"。
        self.public = name
        self.private = "_" + name  # 真正的字符串放在 _name，避免点 name 时又进这个描述符。

    def __get__(self, obj: object, objtype: type | None = None) -> object:
        # 用类去点时 obj 是 None。返回描述符自己，所以类上不是那份字符串。
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj: object, value: str) -> None:
        # 只拒绝空字符串。None 不是这题要拦的对象。
        if value == "":
            raise ValueError("不能为空")
        setattr(obj, self.private, value)


class Person:
    """名字走 NonBlank。类上的 name 和实例上的 name 不是同一种东西。"""

    name = NonBlank()

    def __init__(self, name: str) -> None:
        # 这一行进 NonBlank.__set__。空字符串会在这里失败，对象建不成。
        self.name = name


def main() -> None:
    print("类上", type(Person.name).__name__)
    person = Person("hudi")
    print("实例", person.name)
    try:
        Person("")
    except ValueError as exc:
        print("拒绝", exc)


if __name__ == "__main__":
    main()
