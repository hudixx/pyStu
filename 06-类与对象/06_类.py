"""第 06 课示例：class、self、实例属性、类属性、property。

对照 Java：
- __init__ ≈ 构造方法
- self ≈ this，但必须显式写在参数列表里
- 创建对象没有 new
- 可变类属性会被所有实例共享（类似 static List）
"""


class User:
    """普通用户。species 是类属性，name / years 是实例属性。"""

    species = "human"  # 类似 static，所有 User 共享这一份

    def __init__(self, name: str, years: int) -> None:
        # self 就是正在构造的那个对象，相当于 Java 的 this
        self.name = name
        self._years = years  # 下划线：内部字段，建议通过 property 访问

    @property
    def years(self) -> int:
        """读取年限。外面写 u.years，不会写成 getYears()。"""
        return self._years

    @years.setter
    def years(self, value: int) -> None:
        """赋值时校验。外面写 u.years = 3。"""
        if value < 0:
            raise ValueError("年限不能为负")
        self._years = value

    def introduce(self) -> str:
        """实例方法：第一个参数必须是 self。调用 u.introduce() 时自动传入 u。"""
        return f"我是 {self.name}，学编程 {self.years} 年。"

    def __str__(self) -> str:
        """print(u) 时用，相当于 toString。"""
        return f"User(name={self.name!r}, years={self.years})"


class Team:
    """反例：类属性里放 list，所有队伍共享同一张表。"""

    members: list[str] = []

    def add(self, name: str) -> None:
        self.members.append(name)


class SafeTeam:
    """正例：每个实例在 __init__ 里自己建 list。"""

    def __init__(self) -> None:
        self.members: list[str] = []

    def add(self, name: str) -> None:
        self.members.append(name)


def main() -> None:
    print("=== 创建对象，没有 new ===")
    u = User("hudi", 30)
    print(u.introduce())
    print(u)                 # 走 __str__
    print("类属性:", User.species, u.species)

    print("=== property 赋值校验 ===")
    u.years = 31
    print("改完年限:", u.years)
    try:
        u.years = -1
    except ValueError as exc:
        print("捕获到:", exc)

    print("=== 漏写 self 会长什么样 ===")
    try:
        # 下面这行故意演示：实例方法被当成 0 参数函数调用时的典型报错
        User.introduce()  # 没把实例传进去
    except TypeError as exc:
        print("TypeError:", exc)

    print("=== 可变类属性是坑 ===")
    t1 = Team()
    t2 = Team()
    t1.add("ada")
    print("t2.members =", t2.members)  # ['ada']，t2 根本没 add，却脏了

    s1 = SafeTeam()
    s2 = SafeTeam()
    s1.add("ada")
    print("s2.members =", s2.members)  # []，互不影响


if __name__ == "__main__":
    main()
