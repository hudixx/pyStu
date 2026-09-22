# 第 02 课：从 Java 集合看 Python 容器

Java 里你每天摸 `String`、数组、`ArrayList`、`HashMap`、`HashSet`。
Python 把这些收成 **4 个内置类型**，语法更短，坑也更隐蔽。

先记对照表，再看下面的差异。

| Java | Python | 可变？ | 一句话 |
|---|---|---|---|
| `String` | `str` | 否 | 没有 `char`，`"A"` 也是长度为 1 的字符串 |
| 数组 / `ArrayList` | `list` | 是 | 动态数组，不是链表 |
| 没有直接对应（接近不可变 List / 多返回值） | `tuple` | 否 | 有序、不可变，常用来打包多个值 |
| `HashMap` | `dict` | 是 | 3.7+ 保证插入顺序 |
| `HashSet` | `set` | 是 | 去重、无序（不保证顺序） |

运行示例：

```bash
PYTHONUTF8=1 python 02_容器.py
```

---

## 1. str：很像 String，切片比 substring 强

```python
s = "Python"
s[0]          # 'P'     仍是 str，不是 char
s[-1]         # 'n'     负数下标从右边数，-1 是最后一个
s[0:3]        # 'Pyt'   切片 [起始:结束)，结束下标不包含
s[::2]        # 'Pto'   步长 2
```

和 Java 一样，字符串 **不可变**。`s.replace("P", "J")` 返回新字符串，原来的 `s` 不变。

常用方法对照：

| Java | Python |
|---|---|
| `s.length()` | `len(s)` |
| `s.equals(t)` | `s == t` |
| `s.contains("x")` | `"x" in s` |
| `s.split(",")` | `s.split(",")` |
| `String.join(",", list)` | `",".join(list)` |
| `s.trim()` | `s.strip()` |
| `s.substring(1, 3)` | `s[1:3]` |

注意：`join` 的调用方向和 Java 相反——是 **分隔符.join(可迭代对象)**。

```python
",".join(["a", "b", "c"])  # 'a,b,c'
```

---

## 2. list：把它当 ArrayList，不要当数组

```python
nums = [10, 20, 30]
nums.append(40)      # 类似 add
nums[0] = 99         # 可以改
nums[-1]             # 30 变成 40 之后是 40
```

和 Java 数组 / `ArrayList` 的关键差异：

1. **不必同质**。`[1, "a", None]` 合法，但生产代码里尽量不要混。
2. **`list` 是动态数组**，随机访问 O(1)，头插很慢。需要队列用 `collections.deque`。
3. **切片会得到新 list**（浅拷贝），和 `subList` 那种「视图」不是一回事。

```python
a = [1, 2, 3, 4]
b = a[1:3]     # [2, 3]，b 是新列表
b[0] = 99
# a 仍是 [1, 2, 3, 4]
```

乘法是「重复」，不是把每个元素乘一遍：

```python
[0] * 3        # [0, 0, 0]
[[0] * 3] * 2  # 坑：两个内层 list 其实是同一个对象
```

---

## 3. 最大的坑：`b = a` 不是拷贝

Java 里你已经知道：对象赋值拷的是引用。Python 一样，但因为没有 `new`，更容易忘。

```python
a = [1, 2, 3]
b = a          # b 和 a 指向同一个 list
b.append(4)
# a 也变成 [1, 2, 3, 4]
```

要拷贝：

```python
b = a[:]       # 浅拷贝
b = list(a)    # 浅拷贝
b = a.copy()   # 浅拷贝
```

浅拷贝只复制外层。内层如果还是 list/dict，两边仍共享。
深拷贝用 `copy.deepcopy(a)`，现在知道有这回事即可。

`tuple`、`str`、`int` 不可变，所以 `b = a` 之后你「改 a」其实是让 a 指向新对象，b 不受影响。可变对象才会共享修改。

---

## 4. tuple：不可变的有序列表，常用来打包

```python
point = (3, 4)
x, y = point          # 解包，类似同时声明两个变量
name, years = "hudi", 30
```

函数返回多个值，底层就是在返回 tuple：

```python
def min_max(nums: list[int]) -> tuple[int, int]:
    return min(nums), max(nums)

lo, hi = min_max([3, 1, 9])
```

只有一个元素的 tuple 必须加逗号：`(1,)` 才是 tuple，`(1)` 只是括号里的整数。

---

## 5. dict：就是 HashMap，语法更短

```python
user = {"name": "hudi", "years": 30}
user["name"]              # 没有这个 key 会 KeyError，类似 NPE 之前的那一下
user.get("city")          # 没有则返回 None，不会炸
user.get("city", "未知")  # 类似 getOrDefault
user["city"] = "上海"     # put
"name" in user            # 判断 key 在不在，不看 value
```

遍历：

```python
for key, value in user.items():
    print(key, value)
```

key 必须可哈希：一般用 `str` / `int` / `tuple`。**list 不能当 key**。

Python 3.7+ 的 dict **保留插入顺序**。不要依赖这一点写业务，但打印、测试时会看到稳定顺序。

---

## 6. set：HashSet，用来去重和成员判断

```python
tags = {"python", "java", "python"}  # {'python', 'java'}
tags.add("go")
"java" in tags                       # 成员判断平均 O(1)
```

集合运算和数学一样：

```python
a = {1, 2, 3}
b = {3, 4}
a | b    # 并集
a & b    # 交集
a - b    # 差集
```

空集合必须写 `set()`，`{}` 是空 dict，不是空 set。这个坑 Java 没有。

---

## 7. `==` 和 `is`：equals 与 ==

| Java | Python |
|---|---|
| `equals` 比内容 | `==` 比内容 |
| `==` 比对引用（原始类型除外） | `is` 比是不是同一个对象 |
| `obj == null` | `obj is None`（惯用法） |

```python
a = [1, 2]
b = [1, 2]
a == b     # True，内容相同
a is b     # False，两个 list 对象

x = None
if x is None:   # 判断空值请用 is，不要用 ==
    ...
```

小整数、短字符串有时会被缓存，`is` 碰巧为 True。不要用 `is` 比数值或字符串。

---

## 本课肌肉记忆

1. `list` ≈ `ArrayList`，`dict` ≈ `HashMap`，`set` ≈ `HashSet`，`tuple` 是不可变打包
2. `b = a` 对可变对象是共享引用
3. 切片 `[start:stop]` 含头不含尾，负数下标从右边数
4. `in` 判断成员；dict 的 `in` 只看 key
5. 判空用 `is None`；比内容用 `==`
6. `{}` 是空 dict，空 set 写 `set()`

下一课讲函数参数：`*args` / `**kwargs`、默认参数可变对象这个著名大坑。
