# 第 01 课：从 Java 看 Python

Java 开发者学 Python，最大的障碍不是语法少，而是 **默认假设全错了**。
先把这 8 个心智差异钉住，后面所有课都会轻松很多。

---

## 1. 没有「一个文件必须是一个 public class」

Java：

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("hello");
    }
}
```

Python：文件本身就是可执行脚本。没有强制入口类。

```python
print("hello")
```

想写入口，习惯上用：

```python
def main() -> None:
    print("hello")


# 只有「直接运行这个文件」时才进 main
# 被别人 import 时，这段不会执行
if __name__ == "__main__":
    main()
```

对照：

| Java | Python |
|---|---|
| `public static void main` | `if __name__ == "__main__":` |
| 文件名必须等于 public 类名 | 文件名随意，建议 `snake_case.py` |
| 先编译 `.class` 再跑 | 解释执行，改完直接跑 |

运行方式：

```bash
python 01_hello.py
```

---

## 2. 用缩进代替花括号

这是 Python 最「宗教」的规则：**同一层级必须缩进一致**，官方规范是 **4 个空格**，不要用 Tab。

```python
def greet(name: str) -> None:
    if name:
        print(f"你好, {name}")
    else:
        print("你好, 陌生人")
```

看错一个空格，轻则逻辑错，重则 `IndentationError`。
Java 里花括号包错了还能编译过一部分；Python 缩进就是语法。

---

## 3. 动态类型，但不是没有类型

Java：变量有类型，必须先声明。

```java
String name = "Ada";
int age = 30;
```

Python：名字只是标签，贴在对象上。类型在 **对象** 上，不在变量上。

```python
name = "Ada"   # name 现在指向一个 str
age = 30       # age 指向一个 int
age = "三十"   # 合法，但通常是坏味道
```

现代 Python（3.5+，你的是 3.13）强烈建议写类型注解，给人和 IDE 看，**运行时默认不强制检查**：

```python
def add(a: int, b: int) -> int:
    return a + b
```

对照：

| Java | Python |
|---|---|
| 静态类型，编译期检查 | 动态类型，运行时才爆 |
| `int` 是原始类型 | `int` 也是对象，没有原始类型 |
| `null` | `None`（注意大小写，是单例） |
| `final` / `var` | 没有真正的常量；约定全大写下划线：`MAX_SIZE = 100` |

---

## 4. 没有原始类型，万物皆对象

```java
int x = 1;          // 原始类型
Integer y = 1;      // 装箱
```

Python 里 `1` 就是 `int` 对象：

```python
x = 1
print(type(x))      # <class 'int'>
print(x.bit_length())  # 对象当然有方法
```

这带来一个 Java 直觉会翻车的点：

```python
a = 1
b = a
a = 2
# b 仍然是 1。因为 a = 2 是「让 a 指向新对象」，不是改原来的 1
```

可变对象（list/dict）才是引用共享，下一课细讲。

---

## 5. 布尔与真值，比 Java 更「松」

```python
True   # 注意大写，不是 true
False
None   # 相当于 null
```

`if` 不要求必须是 boolean。下面这些在 `if` 里都算假：

- `None`
- `False`
- `0`、`0.0`
- `""` 空字符串
- `[]`、`{}`、`set()` 空容器

所以：

```python
names = []
if names:          # 相当于 Java 的 !names.isEmpty()
    print("有人")
else:
    print("没人")
```

---

## 6. 字符串：不可变，格式化很香

```python
name = "Ada"
# f-string，Python 3.6+，日常首选
print(f"你好, {name}")

# 多行字符串
sql = """
SELECT *
FROM users
WHERE name = 'Ada'
"""
```

没有 `char` 类型。`"A"` 就是长度为 1 的 `str`。
字符串不可变，类似 Java 的 `String`，没有 `StringBuilder` 那么常用——小拼接直接 `+` 或 f-string 即可。

---

## 7. 注释与文档

```python
# 这是单行注释

def add(a: int, b: int) -> int:
    """两数相加。

    这叫 docstring，相当于 Java 的 Javadoc。
    写在函数/类/模块的第一行。
    """
    return a + b
```

没有 `/* */` 这种真正的块注释。临时注释多行，编辑器快捷键最方便。

---

## 8. 命名与代码风格（PEP 8）

| 用途 | Java | Python |
|---|---|---|
| 变量 / 函数 | `getUserName` | `get_user_name` |
| 类 | `UserService` | `UserService`（一样） |
| 常量 | `MAX_SIZE` | `MAX_SIZE` |
| 私有约定 | `private` 关键字 | 前缀单下划线 `_cache`（约定，不是强制） |
| 包 | `com.foo.bar` | `foo/bar/` 目录 + `__init__.py` |

Python **没有** Java 那种真正的 `private`。单下划线是「请别碰」，双下划线 `__name` 会触发名称改写，初学先只用单下划线。

---

## 本课要建立的肌肉记忆

1. 文件直接跑，不必先建 class
2. 缩进 = 语法
3. 变量是标签，对象才有类型
4. `None` / `True` / `False` 首字母大写
5. 函数和变量用 `snake_case`
6. 入口写成 `if __name__ == "__main__":`

下一课会讲 list / dict / tuple / set——这是你每天都会用、也最容易用 Java 集合类套错的地方。
