# 第 06 课：从 Java 类看 Python 对象

阶段二开始。Python 的 class 看起来眼熟，但有几个习惯必须改：

1. 没有 `new`
2. `this` 必须写成显式参数 `self`
3. 没有强制 `private`，约定用 `_` 开头
4. 日常不写 getter/setter，要用时用 `@property`

运行示例：

```bash
PYTHONUTF8=1 python 06-类与对象/06_类.py
```

---

## 1. 最简对照

Java：

```java
public class User {
    private String name;
    public User(String name) {
        this.name = name;
    }
    public String introduce() {
        return "我是 " + this.name;
    }
}

User u = new User("hudi");
```

Python：

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name          # 实例属性，挂在对象上

    def introduce(self) -> str:
        return f"我是 {self.name}"


u = User("hudi")   # 没有 new
print(u.introduce())
```

| Java | Python |
|---|---|
| 构造方法与类同名 | `__init__` |
| `this` | `self`（必须写在方法第一个参数） |
| `new User(...)` | `User(...)` |
| `private String name;` 先声明 | 通常在 `__init__` 里 `self.name = ...` 当场挂上 |
| getter / setter | 直接 `u.name`，或 `@property` |

`self` 不是关键字，只是约定。写成 `this` 也能跑，但别这么干。
调用 `u.introduce()` 时，Python 自动把 `u` 传进第一个参数，所以你写方法必须留出 `self`。

漏写 `self` 会报：`takes 0 positional arguments but 1 was given`。
这个错 Java 开发者几乎人人都会遇到一次。

---

## 2. 实例属性 vs 类属性

```python
class User:
    species = "human"          # 类属性，类似 static 字段，所有实例共享

    def __init__(self, name: str) -> None:
        self.name = name       # 实例属性，每个对象自己一份
```

可变类属性是坑，和第 03 课默认参数那个坑是亲戚：

```python
class Team:
    members: list[str] = []    # 反例：所有 Team 共享一张表

    def add(self, name: str) -> None:
        self.members.append(name)
```

两个 `Team()` 往里面 `add`，会发现人跑到同一个列表里去了。
正确：在 `__init__` 里 `self.members = []`。

读类属性可以用 `User.species` 或 `u.species`。
**赋值** `u.species = "other"` 不会改类上的那份，而是给这个实例新建一个同名属性。改共享的那份要写 `User.species = ...`。

---

## 3. 可见性：约定，不是编译器强制

| 写法 | 含义 | Java 近似 |
|---|---|---|
| `self.name` | 公开 | `public` |
| `self._cache` | 内部使用，外面别碰 | 包内 / 文档约定 |
| `self.__secret` | 名称改写，防子类覆盖 | 很勉强的 private，日常少用 |

没有真正的 `private`。`u._cache` 在语法上完全合法。
团队靠约定和代码审查，不靠编译器挡。

---

## 4. `@property`：需要 getter 时再请它出山

Python 鼓励直接访问属性：`u.name = "ada"`。
只有「读取时要计算」或「赋值时要校验」，才用 property：

```python
class User:
    def __init__(self, years: int) -> None:
        self._years = years

    @property
    def years(self) -> int:
        return self._years

    @years.setter
    def years(self, value: int) -> None:
        if value < 0:
            raise ValueError("年限不能为负")
        self._years = value
```

外面仍然写成 `u.years`、`u.years = 3`，没有 `getYears()`。
这相当于 Lombok 的 `@Getter`，但只有你真需要逻辑时才写。

---

## 5. `__str__` / `__repr__` ≈ `toString`

```python
def __str__(self) -> str:
    return f"User({self.name})"
```

`print(u)` 走 `__str__`。
`__repr__` 给开发和调试看，交互式环境里直接敲变量名走它。两边都写也可以，基础阶段先写 `__str__`。

---

## 6. 预告：`@dataclass` ≈ Lombok `@Data` / Java Record

字段多、只是装数据时：

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    years: int
```

自动生成 `__init__`、`__repr__`、比较方法。后面会用到，现在知道有这东西即可。

---

## 本课肌肉记忆

1. 创建对象没有 `new`：`User("hudi")`
2. 方法第一个参数必须是 `self`，调用时不用传
3. 实例属性在 `__init__` 里 `self.xxx = ...`
4. 可变对象不要当类属性，放到 `__init__` 里
5. `_name` 是约定私有；日常直接 `u.name`，少写 getter
6. 需要计算或校验再用 `@property`

下一课讲继承、鸭子类型，对照 `interface` / `abstract` / 多态。
