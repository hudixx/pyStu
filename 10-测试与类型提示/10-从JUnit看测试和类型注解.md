# 第 10 课：从 JUnit 看测试和类型注解

Java：JUnit + 泛型在编译期帮你挡错。
Python：类型注解默认 **不在运行时检查**；测试用标准库 `unittest`（永远能跑），社区更常用 `pytest`。

运行示例：

```bash
PYTHONUTF8=1 python 10-测试与类型提示/10_类型与测试.py
PYTHONUTF8=1 python -m unittest 10-测试与类型提示/test_demo.py
```

在 `10-测试与类型提示` 目录下跑 unittest 更省事：

```bash
cd 10-测试与类型提示
PYTHONUTF8=1 python -m unittest test_demo.py
```

---

## 1. 类型注解：给人和 IDE 看，不是给编译器看

```python
def add(a: int, b: int) -> int:
    return a + b

add("x", "y")  # 运行时能拼成 "xy"，注解挡不住
```

常见写法（3.9+ / 你的 3.13 全部可用）：

| 含义 | 写法 | Java 近似 |
|---|---|---|
| 可空 | `str \| None` | `@Nullable String` |
| 列表 | `list[int]` | `List<Integer>` |
| 字典 | `dict[str, int]` | `Map<String, Integer>` |
| 元组定长 | `tuple[str, int]` | 没有直接对应 |
| 可变参数 | `*args: str` | `String...` |
| 任意对象 | `object` | `Object` |
| 还不知道 | `Any`（`from typing import Any`） | 能不用就不用 |

`Optional[str]` 和 `str | None` 等价，新代码用 `|`。

注解不会让错误代码跑不起来。要拦，得靠：

- IDE（PyCharm / Pylance）
- 独立检查器 `mypy` / `pyright`（需另装，本课不强制）

把注解写上，仍然值得：IDE 补全、你自己读代码、后面接 mypy 都靠它。

---

## 2. `unittest` ≈ JUnit 4 的味道

```python
import unittest
from stats import average

class TestAverage(unittest.TestCase):
    def test_normal(self) -> None:
        self.assertEqual(average([2, 4]), 3.0)

    def test_empty(self) -> None:
        with self.assertRaises(ValueError):
            average([])

if __name__ == "__main__":
    unittest.main()
```

| JUnit | unittest |
|---|---|
| `@Test` | 方法名以 `test_` 开头 |
| `assertEquals` | `self.assertEqual` |
| `assertTrue` | `self.assertTrue` |
| `assertThrows` | `self.assertRaises` |
| `@BeforeEach` | `setUp` |
| `@AfterEach` | `tearDown` |
| `@BeforeAll` | `setUpClass`（要 `@classmethod`） |

运行：`python -m unittest test_demo.py -v`

---

## 3. `pytest`：社区默认，语法更短

需要先装（在已激活的 `.venv` 里）：

```bash
python -m pip install pytest
```

```python
import pytest
from stats import average

def test_normal() -> None:
    assert average([2, 4]) == 3.0

def test_empty() -> None:
    with pytest.raises(ValueError):
        average([])
```

普通函数 + `assert` 即可，不必继承 TestCase。
本课练习 **用 unittest**，不强制装 pytest。知道有这东西、以后项目里更常见即可。

---

## 4. 测试习惯（和 Java 一样）

1. 一个测试测一件事
2. 名字说清楚场景：`test_empty_list_raises` 好过 `test1`
3. 测正常路径，也测异常路径
4. 不要测 Python 语言本身（不必 `assert 1 + 1 == 2`）
5. 测试文件名 `test_*.py`，方便发现

---

## 本课肌肉记忆

1. 注解是文档和 IDE 契约，运行时默认不强制
2. `str | None` 代替 `Optional[str]`
3. `unittest` 在标准库，方法名 `test_` 开头
4. `assertRaises` 测异常
5. pytest 更流行，但要 pip 安装
6. 空列表、边界、抛异常，这些路径都要覆盖

下一课讲迭代器、生成器、装饰器——Python 比 Java 写起来短一截的地方。
