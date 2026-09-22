# 第 08 课：从 Java 异常看 try / except / with

Java 有检查异常（`throws IOException`），编译器逼你处理。
Python **没有检查异常**。想抛就 `raise`，想接就 `except`，编译器不管。
资源释放对应 Java 的 try-with-resources，Python 用 `with`。

运行示例：

```bash
PYTHONUTF8=1 python 08-异常与上下文管理器/08_异常.py
```

---

## 1. 对照表

| Java | Python |
|---|---|
| `try / catch / finally` | `try / except / else / finally` |
| `throw new IllegalArgumentException(...)` | `raise ValueError(...)` |
| `catch (ValueError e)` | `except ValueError as e` |
| 检查异常必须声明 `throws` | 没有检查异常 |
| try-with-resources | `with ... as ...` |
| `e.getMessage()` | `str(e)` 或 `e.args` |

`else` 是 Python 多出来的：`try` 里 **没发生异常** 才走 `else`。
不要和 `for/else` 搞混，但思路类似——「善终才进 else」。

```python
try:
    n = int("12")
except ValueError as e:
    print("转换失败", e)
else:
    print("成功", n)      # 没进 except 才会到这里
finally:
    print("一定执行")
```

---

## 2. 没有检查异常，意味着什么

Java：

```java
public String read() throws IOException { ... }
```

调用方必须 `catch` 或继续 `throws`。

Python：函数签名上不声明会抛什么。调用方愿意接就接，不接就一路冒到顶，打印 traceback。

常见内置异常（都是 `Exception` 的子类）：

| 异常 | 典型原因 | Java 近似 |
|---|---|---|
| `ValueError` | 值不合法，如 `int("abc")` | `IllegalArgumentException` |
| `TypeError` | 类型不对 | `ClassCastException` 一类 |
| `KeyError` | dict 缺 key | 有点像 NPE 之前的那一下 |
| `IndexError` | 下标越界 | `IndexOutOfBoundsException` |
| `AttributeError` | 没有这个属性/方法 | 鸭子类型失败时最常见 |
| `FileNotFoundError` | 文件不存在 | `FileNotFoundException` |
| `ZeroDivisionError` | 除以 0 | `ArithmeticException` |

自己定义异常：继承 `Exception`（不要继承 `BaseException`，那是给系统退出用的）。

```python
class BalanceError(Exception):
    """余额不足。"""
```

`except` 要写具体类型。`except Exception:` 相当于 Java 裸 `catch (Exception e)`，能用，但会把你没想到的 bug 也吃掉。多个 `except` 时 **子类写在前面**，否则永远进父类分支。

---

## 3. `raise` 和异常链

```python
raise ValueError("年限不能为负")

try:
    int("x")
except ValueError as e:
    raise RuntimeError("配置错误") from e   # 保留原因，类似 e.initCause
```

光写 `raise`（except 块里不带参数）会把当前异常原样再抛出去，类似 Java 的裸 `throw;`。

---

## 4. `with` = try-with-resources

Java：

```java
try (BufferedReader r = Files.newBufferedReader(path)) {
    return r.readLine();
}
```

Python：

```python
with open("a.txt", encoding="utf-8") as f:
    text = f.read()
# 离开 with 块，文件一定关，哪怕中途报错
```

原理：对象实现了上下文管理器协议：

- `__enter__`：进入 `with` 时调用，返回值赋给 `as` 后面的变量
- `__exit__`：离开时调用（含异常情况），负责清理

自己也可以写：

```python
class Closer:
    def __enter__(self):
        print("打开")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        print("关闭")
        return False  # False 表示不吞掉异常，让它继续冒
```

`from contextlib import contextmanager` 能用生成器更短地写，下一阶段再展开。现在先会 `with open` 和「离开块 = 释放资源」。

---

## 5. EAFP：Python 更喜欢先做，再捕获

Java 常 LBYL（Look Before You Leap）：先判断再动手。

```java
if (map.containsKey(k)) {
    return map.get(k);
}
```

Python 常 EAFP（Easier to Ask Forgiveness than Permission）：

```python
try:
    return data[k]
except KeyError:
    return default
```

dict 更惯用 `data.get(k, default)`，不必真写 try。但文件、网络、转换这类「问了也可能在两行之间变化」的操作，用 try/except 更自然。

---

## 本课肌肉记忆

1. `throw` → `raise`；`catch` → `except ... as`
2. 没有检查异常，签名上不用声明 `throws`
3. `try/except/else/finally`：else 表示 try 成功
4. 自己的异常继承 `Exception`
5. `with` 对标 try-with-resources，文件用 `open` 必须配 `with`
6. 先做再捕获（EAFP），不要每个调用都先 `if` 问一遍

下一课讲文件、路径、JSON，对照 `Files` / `Path` / Jackson。
