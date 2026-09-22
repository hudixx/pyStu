# 第 05 课：从 Maven 看 Python 模块、包、虚拟环境

Java 项目靠 `package` + classpath + Maven。
Python 对应三件套：**模块 / 包 / 虚拟环境**。

本课示例请在本目录下运行（否则找不到旁边的 `greet.py`）：

```bash
cd 05-模块包与虚拟环境
PYTHONUTF8=1 python 05_模块.py
```

---

## 1. 一个 `.py` 文件就是一个模块

| Java | Python |
|---|---|
| `Hello.java` 里的 `public class Hello` | `greet.py` 里的函数/类 |
| `import com.foo.Hello;` | `import greet` |
| `import static com.foo.Hello.hi;` | `from greet import hello` |
| 类名别名没有语言级支持 | `from greet import hello as hi` |

```python
import greet                 # 用 greet.hello(...)
from greet import hello      # 直接 hello(...)
from greet import hello as hi
```

加载模块时，文件顶层代码会执行一遍（包括 `def`，也包括你不小心写在外面的 `print`）。
所以入口逻辑必须放进 `if __name__ == "__main__":`。这就是第 01 课那句的真正用途：

| 怎么用这个文件 | `__name__` 的值 |
|---|---|
| `python greet.py` 直接跑 | `"__main__"` |
| `import greet` | `"greet"` |

---

## 2. 目录 + `__init__.py` = 包

```text
tools/
    __init__.py    # 包的门面，可以为空
    text.py        # 子模块
```

```python
from tools.text import shout
from tools import shout      # 如果 __init__.py 里转出了 shout
```

对照：

| Java | Python |
|---|---|
| `package com.foo.tools;` | 目录 `tools/` |
| 目录必须和 package 声明一致 | 目录名就是包名，没有 package 声明 |
| `com/foo/tools/Text.java` | `tools/text.py` |
| 没有 `__init__` 这种文件 | `__init__.py` 让目录成为包 |

`from module import *` 和 Java 的 `import static ...*` 一样，生产代码别用，会污染命名空间。

---

## 3. `sys.path` ≈ classpath

Python 找模块时按 `sys.path` 从上往下搜，很像 classpath：

1. 被运行脚本所在目录
2. `PYTHONPATH` 环境变量
3. 标准库
4. 第三方包（site-packages，通常在虚拟环境里）

所以你在别的目录运行 `python 05_模块.py`，有时能跑（脚本目录会被加进 path），
自己再 `import greet` 的练习文件如果放错位置就会 `ModuleNotFoundError`。
报这个错，先想：我是从哪个目录启动的？模块在不在 `sys.path` 里？

---

## 4. 虚拟环境 ≈ 每个项目一份独立的「JDK + 本地仓库」

Java 一个项目一份 `pom.xml`，依赖进本地 `.m2`，用的 JDK 可以全局装。
Python 全局只有一套解释器时，`pip install` 会把包装到系统 Python 里，项目互相踩脚。

解决办法：每个项目一个 **venv**。

```bash
# 在项目根目录 pyStu 下执行
python -m venv .venv
```

激活（你现在用的是 Git Bash）：

```bash
source .venv/Scripts/activate
```

激活成功后，提示符前面会出现 `(.venv)`，此时 `python` 和 `pip` 都指向这个环境。

| 动作 | Java | Python |
|---|---|---|
| 声明依赖 | `pom.xml` | `requirements.txt` 或 `pyproject.toml` |
| 安装依赖 | `mvn install` | `pip install -r requirements.txt` |
| 隔离 | 主要靠 Maven 坐标 | 靠 venv 把 site-packages 隔开 |
| 别用全局乱装 | 别改系统 JDK 的 lib | 别对系统 Python 直接 `pip install` |

`requirements.txt` 长这样：

```text
requests==2.32.3
```

它只是一份「装哪些包」的清单，**没有 Maven 那么完整的传递依赖锁定**。
现代项目更常用 `pyproject.toml` + `uv` / `poetry`。基础阶段先会 `venv` + `pip` 就够。

Windows 上建议始终：

```bash
python -m pip install ...
```

而不是裸 `pip`，避免装到另一个 Python 身上。

退出虚拟环境：

```bash
deactivate
```

---

## 5. 标准库先于第三方

Python 自带很多「JDK 里就有」的东西，先查标准库再 `pip install`：

| 需求 | 先看标准库 |
|---|---|
| 路径 | `pathlib` |
| JSON | `json` |
| 时间 | `datetime` |
| 正则 | `re` |
| HTTP 客户端 | `urllib`（第三方常用 `requests` / `httpx`） |
| 单元测试 | `unittest`（第三方常用 `pytest`） |

`pip install requests` 之前问自己：标准库有没有？

---

## 本课肌肉记忆

1. `.py` 文件 = 模块；目录 + `__init__.py` = 包
2. `import x` 用 `x.f()`；`from x import f` 直接 `f()`
3. `__name__ == "__main__"` 区分「当入口」还是「被导入」
4. `ModuleNotFoundError` 先查启动目录和 `sys.path`
5. 每个项目建 `.venv`，不要往系统 Python 里乱装包
6. `python -m pip` 比裸 `pip` 更安全

阶段一到此结束。下一课开始阶段二：类、对象、`self`，对照 Java 的 class / this / getter。
