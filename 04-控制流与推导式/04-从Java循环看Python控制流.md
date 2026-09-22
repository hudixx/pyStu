# 第 04 课：从 Java 循环看 Python 控制流

Java 写循环，脑子里常是下标：`for (int i = 0; i < n; i++)`。
Python 默认按 **元素** 遍历；需要下标时再请 `enumerate` 出山。
过滤和变换，Java 用 Stream，Python 用 **推导式**（comprehension）。

运行示例：

```bash
PYTHONUTF8=1 python 04_控制流.py
```

---

## 1. if / elif / else

`else if` 在 Python 里写成一个词 `elif`：

```python
if score >= 90:
    grade = "A"
elif score >= 60:
    grade = "B"
else:
    grade = "C"
```

---

## 2. 三元表达式：顺序和 Java 相反

Java：`cond ? 真值 : 假值`

Python：

```python
label = "正" if n > 0 else "非正"
```

先写结果，再写条件。刚从 Java 过来时最容易把顺序写反。
只适合短表达式。分支一复杂，老实用 `if/else`。

---

## 3. for 遍历的是元素，不是下标

```java
for (String lang : langs) {
    System.out.println(lang);
}
```

```python
for lang in langs:
    print(lang)
```

几乎一一对应。不要一上来就写 `for i in range(len(langs))`，那是 Java 下标习惯的翻译腔。

真需要下标，用 `enumerate`：

```python
for index, lang in enumerate(langs):
    print(index, lang)

# 下标从 1 开始数：
for index, lang in enumerate(langs, start=1):
    print(index, lang)
```

`range(n)` 产生 `0 .. n-1`，类似但不必先造一个列表：

```python
for i in range(3):      # 0, 1, 2
    ...
for i in range(1, 4):   # 1, 2, 3
    ...
for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    ...
```

`zip` 把几条序列并排走，最短的那条走完就停：

```python
names = ["hudi", "ada"]
years = [30, 1]
for name, year in zip(names, years):
    print(name, year)
```

---

## 4. `for` / `while` 也可以带 `else`（Python 独有）

循环 **没有被 break 打断** 时，才执行 `else`。可以把它读成「循环善终」。

```python
needle = "go"
for lang in ["java", "python"]:
    if lang == needle:
        print("找到了")
        break
else:
    print("没找到")  # 全程没 break，才会进这里
```

Java 没有这个结构，一般要另设一个 `boolean found`。看到 `for/else` 别当成「循环完再走 else 分支」——**被 break 过就不会进 else**。

---

## 5. 推导式：Python 版的 Stream map / filter

Java：

```java
list.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .toList();
```

Python 一行：

```python
squares = [n * n for n in nums if n % 2 == 0]
```

读法从左到右：**要什么 + 从哪来 + 过滤条件**。

| 写法 | 含义 |
|---|---|
| `[x * 2 for x in nums]` | map |
| `[x for x in nums if x > 0]` | filter |
| `[x * 2 for x in nums if x > 0]` | filter + map |
| `{x for x in nums}` | 得到 set，自动去重 |
| `{k: v.upper() for k, v in user.items()}` | 得到 dict |

推导式里只放表达式，不要放 `print`、`append` 这种副作用。那种情况用普通 `for`。

圆括号是 **生成器表达式**，惰性的，下一阶段再细讲：

```python
sum(n * n for n in nums)  # 不先造完整列表
```

---

## 6. `match` / `case`（3.10+，你的 3.13 可以用）

类似 Java 的 `switch`，但能拆结构。现在先知道有这东西：

```python
match grade:
    case "A":
        print("优秀")
    case "B" | "C":
        print("及格")
    case _:
        print("其它")
```

基础阶段用 `if/elif` 就够。

---

## 本课肌肉记忆

1. `elif` 不是 `else if`
2. 三元是 `真值 if 条件 else 假值`，和 Java 顺序相反
3. `for x in xs` 优先；要下标用 `enumerate`，不要 `range(len(...))`
4. `for/else` 的 else 表示「没被 break」
5. 推导式 = 要什么 for 从哪来 if 过滤
6. 推导式里不要写副作用

下一课讲模块、包、虚拟环境，对照 Java 的 package / Maven。
