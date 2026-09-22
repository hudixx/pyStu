# 第 07 课：从 Java 接口看继承、协议、鸭子类型

Java 靠 `extends` + `implements` 把类型关系钉死在编译期。
Python 也能继承，但日常更常见的是：**只要有这个方法，就算同一类东西**——鸭子类型。

运行示例：

```bash
PYTHONUTF8=1 python 07-继承与鸭子类型/07_继承.py
```

---

## 1. 单继承：看起来最像 Java

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):          # 相当于 extends Animal
    def speak(self) -> str:  # 覆盖父类方法
        return f"{self.name}: 汪"
```

子类要调用父类构造，写 `super().__init__(...)`，相当于 Java 的 `super(...)`。
`super()` 不用传 class / this，普通单继承这样写即可。

覆盖时，Python 3.12+（你是 3.13）可以加 `@override`，给人和 IDE 看，运行时默认不强制：

```python
from typing import override

class Dog(Animal):
    @override
    def speak(self) -> str:
        return f"{self.name}: 汪"
```

---

## 2. 没有 `implements`：鸭子类型

Java 必须先有接口，才能当参数：

```java
void greet(Speaker s) { s.speak(); }
```

Python 函数参数不声明类型也能跑。调用 `obj.speak()` 时，只要这个对象 **真的有 speak 方法** 就行，不必有共同父类：

```python
class Dog:
    def speak(self) -> str:
        return "汪"


class Robot:
    def speak(self) -> str:
        return "哔哔"


def greet(speaker) -> None:
    print(speaker.speak())  # Dog 和 Robot 都能传进来


greet(Dog())
greet(Robot())
```

这叫鸭子类型：走起路来像鸭子、叫起来像鸭子，那它就是鸭子。
类型检查器（IDE / mypy）看不到共同父类，可能划警告，但 **运行时完全合法**。

代价：没有接口时，拼错方法名要到运行时才 `AttributeError`。
Java 那种「忘了实现接口方法，编译不过」的保护，这里默认没有。

---

## 3. 需要「像接口」时：`Protocol` 或 `ABC`

两种工具，用途不同。

**Protocol（结构化类型，推荐给类型检查看）** ≈ Java interface，但 **不用显式 implements**。
只要方法签名对得上，就算满足：

```python
from typing import Protocol

class Speaker(Protocol):
    def speak(self) -> str: ...


def greet(speaker: Speaker) -> None:
    print(speaker.speak())
```

`Dog` 不用写 `class Dog(Speaker)`。IDE / mypy 会按结构检查。运行时几乎什么都不做。

**ABC（抽象基类）** ≈ Java abstract class。想 **强制子类必须实现**，用它：

```python
from abc import ABC, abstractmethod

class Speaker(ABC):
    @abstractmethod
    def speak(self) -> str:
        raise NotImplementedError


class Dog(Speaker):
    def speak(self) -> str:
        return "汪"
```

漏写 `speak` 时，`Dog()` 会立刻 TypeError，这才接近 Java 抽象类的感觉。

基础阶段记口诀：

- 只是想让 IDE 帮忙 → `Protocol`
- 必须拦住「没实现就实例化」→ `ABC`
- 小脚本、两边都是你写的代码 → 直接鸭子类型

---

## 4. `isinstance` 仍然有用，但别当第一选择

```python
isinstance(dog, Animal)     # True
isinstance(dog, Dog)        # True
issubclass(Dog, Animal)     # True
```

Java 里 `instanceof` 很常见。Python 里优先问「它有没有这个方法」，而不是「它是不是某个类的实例」。
真正需要分支时再用 `isinstance`。

---

## 5. 多重继承：Java 没有 class 多重继承，Python 有

```python
class Loggable:
    def log(self, msg: str) -> None:
        print(msg)


class Timestamped:
    def now(self) -> str:
        return "12:00"


class Service(Loggable, Timestamped):
    pass
```

查找方法时按 **MRO**（Method Resolution Order）从左到右。`Service.__mro__` 可以打印出来看。
现在知道「可以多重继承、有顺序」即可，不要为了炫技去用。能组合（对象里塞另一个对象）就别多重继承。

---

## 本课肌肉记忆

1. `class Dog(Animal):` + `super().__init__(...)` 覆盖父类
2. 不必有共同父类，有同名方法就能当同一类东西用（鸭子类型）
3. 给类型检查看用 `Protocol`；要强制实现用 `ABC`
4. 优先问「有没有这个方法」，少问「是不是这个类」
5. 多重继承存在，但组合优于继承——这点和 Java 一样

下一课讲异常和 `with`，对照 `try/catch/finally` 和 try-with-resources。
