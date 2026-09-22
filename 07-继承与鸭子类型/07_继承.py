"""第 07 课示例：继承、super、鸭子类型、Protocol、ABC。

对照 Java：
- class Dog(Animal) ≈ extends
- 没有 implements，靠鸭子类型
- Protocol ≈ 结构化的 interface（不用显式声明实现）
- ABC ≈ abstract class
"""

from abc import ABC, abstractmethod
from typing import Protocol, override


class Animal:
    """普通父类，方法可以有默认实现。"""

    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name}: ..."


class Dog(Animal):
    """单继承。覆盖 speak，构造时把 name 交给父类。"""

    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)  # 相当于 Java 的 super(name)
        self.breed = breed

    @override
    def speak(self) -> str:
        return f"{self.name}（{self.breed}）: 汪"


class Robot:
    """和 Animal 毫无继承关系，但有 speak，就能当「会叫的东西」。"""

    def speak(self) -> str:
        return "哔哔"


def greet(speaker) -> None:
    """鸭子类型：不检查类型，只调用 speak。"""
    print(speaker.speak())


class Speaker(Protocol):
    """给 IDE / mypy 看的接口。运行时不强制任何人继承它。"""

    def speak(self) -> str: ...


def greet_typed(speaker: Speaker) -> None:
    """注解写成 Speaker 后，Dog / Robot 都算合法（结构匹配）。"""
    print(speaker.speak())


class Shape(ABC):
    """抽象基类：子类必须实现 area，否则连实例化都不让。"""

    @abstractmethod
    def area(self) -> float:
        raise NotImplementedError


class Square(Shape):
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side * self.side


def main() -> None:
    print("=== 继承 + super ===")
    dog = Dog("旺财", "土狗")
    print(dog.speak())
    print("isinstance(dog, Animal) =", isinstance(dog, Animal))

    print("=== 鸭子类型：没有共同父类也能 greet ===")
    greet(dog)
    greet(Robot())
    greet_typed(Robot())  # Protocol 按结构认，不必 class Robot(Speaker)

    print("=== ABC：没实现就不能实例化 ===")
    print("Square 面积 =", Square(3).area())
    try:
        Shape()  # 抽象类不能直接 new / 直接调用
    except TypeError as exc:
        print("TypeError:", exc)

    print("=== MRO（多重继承时的查找顺序）===")
    print(Dog.__mro__)


if __name__ == "__main__":
    main()
