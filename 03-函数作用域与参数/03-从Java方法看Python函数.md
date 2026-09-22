# 第 03 课：从 Java 方法看 Python 函数

Java 的方法待在类里，靠重载区分参数。
Python 的函数是一等公民：可以当参数传、当返回值、赋给变量。没有重载，用默认参数和 `*args` / `**kwargs` 顶。

运行示例：

```bash
PYTHONUTF8=1 python 03_函数.py
```

---

## 1. 没有方法重载，后写的会盖掉先写的

Java：

```java
void greet() { ... }
void greet(String name) { ... }
```

Python 不允许两份同名 `def` 和平共存。后定义的直接覆盖前面那个：

```python
def greet(name: str = "陌生人") -> None:
    print(f"你好, {name}")

greet()
greet("hudi")
```

一个函数 + 默认参数，就覆盖了 Java 里好几份重载。

---

## 2. 默认参数的著名大坑：可变对象不要当默认值

```python
def add_item(item: str, bucket: list[str] = []) -> list[str]:
    bucket.append(item)
    return bucket
```

`[]` 这个默认列表 **只在 def 时创建一次**，以后每次调用都复用同一张表。
这和 Java 每次进方法 `new ArrayList<>()` 完全相反。

正确写法：默认用 `None`，函数里面再新建。

```python
def add_item(item: str, bucket: list[str] | None = None) -> list[str]:
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

规则：**默认参数只写不可变的**（`None`、`int`、`str`、`tuple`）。`list` / `dict` / `set` 不要放默认值。

---

## 3. `*args` 相当于 varargs，`**kwargs` Java 没有直接对应

```java
void log(String... msgs) { ... }
```

```python
def log(*args: str) -> None:
    # args 是一个 tuple，装下所有多出来的位置参数
    for item in args:
        print(item)


def connect(host: str, **kwargs) -> None:
    # kwargs 是一个 dict，装下所有多出来的关键字参数
    port = kwargs.get("port", 3306)
    print(host, port)
```

调用：

```python
log("a", "b", "c")
connect("localhost", port=5432, timeout=10)
```

`*` 和 `**` 也可以用在调用处，把容器拆开：

```python
nums = [1, 2, 3]
print(*nums)            # 等价 print(1, 2, 3)

user = {"name": "hudi", "years": 30}
# 下面假设函数是 def introduce(name, years)
# introduce(**user)
```

---

## 4. 传参模型和 Java 一样：传的是对象的引用

Java 是「引用的值传递」。Python 官方说法是 **传对象引用**（pass by assignment），体感几乎一样：

- 传 `int` / `str` / `tuple`：函数里 `x = 新值` 改的是局部标签，外面看不到
- 传 `list` / `dict`：函数里 `x.append(...)` 改的是同一个对象，外面看得到

```python
def append_bang(items: list[str]) -> None:
    items.append("!")      # 外面那张表会被改掉


def rebind(items: list[str]) -> None:
    items = ["全新"]       # 只是把局部标签撕下来，外面那张表不动
```

这和第 02 课的 `b = a` 是同一件事。

---

## 5. Python 没有块级作用域（Java 开发者最容易踩）

Java：

```java
if (true) {
    int x = 1;
}
// x 在这里不存在
```

Python：`if` / `for` / `while` **不会**新建一层变量作用域。

```python
if True:
    x = 1
print(x)        # 1，出了 if 还能用

for i in range(3):
    pass
print(i)        # 2，循环变量泄漏到外面
```

Python 的作用域只有这些层（LEGB）：

| 层 | 含义 | Java 近似 |
|---|---|---|
| L Local | 当前函数内 | 方法内局部变量 |
| E Enclosing | 外层函数 | 内部类 / lambda 捕获 |
| G Global | 当前模块 | 类的 static 字段（勉强比） |
| B Built-in | `len` / `print` 这些 | JDK 自带 |

函数里想给模块级变量赋值，要写 `global name`。
嵌套函数里想改外层函数的变量，要写 `nonlocal name`。
现在先记住：**读外面可以，赋值默认只改局部。**

---

## 6. 函数是对象，lambda 只能写一条表达式

```python
def add(a: int, b: int) -> int:
    return a + b

op = add            # 函数可以当值传来传去
print(op(1, 2))     # 3

# lambda 相当于极简匿名函数，只能是表达式，不能有语句
double = lambda n: n * 2
print(double(5))    # 10
```

Java 的 lambda 能写代码块 `{ ... }`。Python 的 `lambda` 不能。稍复杂就老老实实 `def`。

---

## 本课肌肉记忆

1. 不要写两份同名 `def`，用默认参数代替重载
2. 默认值不要放 `list` / `dict`，放 `None` 再在函数里创建
3. `*args` 是 tuple，`**kwargs` 是 dict
4. 传 list 进去再 `append`，外面会被改；重新赋值不会
5. `if` / `for` 不形成新作用域，循环变量会漏出来
6. 函数可以当参数传；`lambda` 只适合特别短的表达式

下一课讲 `for` / 推导式，对照 Java 的增强 for 和 Stream。
