# 第 11 课：从 Stream 和 AOP 看 yield 与装饰器

Java 的 `Iterator` / Stream 惰性拉数据；Spring 的 `@Transactional` 一类注解在方法外包一层。
Python 对应两件更轻的语法：**生成器（`yield`）** 和 **装饰器（`@`）**。

运行示例：

```bash
PYTHONUTF8=1 python 11-迭代器生成器与装饰器/11_生成器与装饰器.py
```

---

## 1. `for` 的背后是迭代器

```python
for x in [1, 2, 3]:
    print(x)
```

等价于：取迭代器 → 反复 `next()` → 直到 `StopIteration`。

自己实现迭代器要写 `__iter__` + `__next__`，很少手写。
日常用生成器函数即可，Python 帮你做成迭代器。

---

## 2. 生成器：`yield` 暂停函数

```python
def countdown(n: int):
    while n > 0:
        yield n     # 把 n 交出去，函数在这里暂停
        n -= 1
```

```python
for x in countdown(3):
    print(x)        # 3 2 1
```

| `return` | `yield` |
|---|---|
| 函数结束，交一个值 | 函数暂停，交一个值，下次从这里继续 |
| 马上占用全部结果内存 | 一次产一个，惰性 |

Java Stream 的惰性、`Iterator.next()` 的「拉模型」，在 Python 里最自然的写法就是 `yield`。

生成器表达式（惰性版推导式）：

```python
sum(x * x for x in range(10) if x % 2 == 0)
```

圆括号不是 tuple，是生成器。大文件、大范围不要先 `[...]` 做成完整列表。

`yield from` 可以把另一个可迭代对象委托出去，现在知道有这回事即可。

---

## 3. 装饰器：把函数包一层，对标 AOP 注解

```python
def logged(func):
    def wrapper(*args, **kwargs):
        print("调用", func.__name__)
        return func(*args, **kwargs)
    return wrapper


@logged
def add(a: int, b: int) -> int:
    return a + b
```

`@logged` 等价于 `add = logged(add)`。
调用 `add(1, 2)` 时，实际跑的是 `wrapper`。

这和 Spring `@Transactional` / `@Cacheable` 同一思路：不改业务函数本身，在外面加行为。
差别：Python 装饰器就是函数，没有代理框架那么重。

完整、可复用的写法：

```python
from functools import wraps

def logged(func):
    @wraps(func)          # 把原函数的名字、doc 拷过来
    def wrapper(*args, **kwargs):
        print("调用", func.__name__)
        return func(*args, **kwargs)
    return wrapper
```

带参数的装饰器是「三层」：外层收参数，中层收函数，内层收调用。基础阶段会写无参装饰器就够。

你已经用过的 `@property`、`@override`、`@abstractmethod` 都是装饰器。

---

## 4. 常见坑

1. 生成器只能向前走，不能像 list 那样 `g[0]` 或反复遍历（走完就空了）
2. 装饰器漏 `@wraps`，函数名会变成 `wrapper`，测试和日志难看
3. 装饰器里要 `return func(...)` 的返回值，别吞掉
4. 对实例方法加装饰器时，`wrapper` 的第一个参数仍是 `self`，用 `*args` 最省事

---

## 本课肌肉记忆

1. `yield` 产出惰性序列，对标 Stream / Iterator
2. 生成器表达式用圆括号，列表推导用方括号
3. `@deco` 就是 `f = deco(f)`
4. 装饰器用 `*args, **kwargs` 转发，记得返回原函数的返回值
5. 用 `functools.wraps` 保住原函数元数据

下一课讲并发和 GIL——Java 线程直觉在 CPython 里会失效的地方。
