# 第 13 课：从 JDK 和 Maven 看标准库与 pip

Java：JDK 很大，缺的去 Maven Central。
Python：**标准库已经很能打**，先查标准库再 `pip install`。第三方生态在 PyPI，用 pip 装进 **当前 venv**。

运行示例：

```bash
PYTHONUTF8=1 python 13-标准库与生态/13_标准库.py --name hudi
```

---

## 1. 先翻标准库这张表

| 需求 | 模块 | Java 近似 |
|---|---|---|
| 路径 / 文件 | `pathlib` | `Path` / `Files` |
| JSON | `json` | Jackson 的一个子集 |
| 命令行参数 | `argparse` | `main(String[] args)` + picocli |
| 时间 | `datetime` / `zoneinfo` | `LocalDateTime` / `Instant` |
| 计数 / 缺省 dict | `collections.Counter` / `defaultdict` | 自己写或 Guava |
| 迭代工具 | `itertools` | Stream 的一部分 |
| 正则 | `re` | `Pattern` |
| 日志 | `logging` | `java.util.logging` / slf4j |
| 随机 | `random` | `Random` |
| HTTP 客户端 | `urllib.request` | `HttpClient`（能用但啰嗦） |

第三方里几乎人人会装的：

| 包 | 干什么 |
|---|---|
| `requests` / `httpx` | 人话版 HTTP |
| `pytest` | 测试 |
| `rich` | 终端漂亮输出 |
| `pydantic` | 数据校验 |
| FastAPI / Django | Web（对标 Spring） |
| pandas | 表格数据 |

本课 **不强制 pip install**。先把标准库用熟。

---

## 2. `argparse`：正规的命令行

```python
parser = argparse.ArgumentParser(description="演示")
parser.add_argument("--name", default="陌生人")
parser.add_argument("--times", type=int, default=1)
args = parser.parse_args()
print(args.name, args.times)
```

```bash
python 13_标准库.py --name hudi --times 3
python 13_标准库.py -h
```

不要为了图快自己解析 `sys.argv`，除非参数只有一个。

---

## 3. `datetime`

```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Shanghai"))
later = now + timedelta(days=1)
print(now.strftime("%Y-%m-%d %H:%M:%S"))
```

`datetime.now()` 不带时区容易埋坑。需要「此刻」就给时区。
`datetime` 对象默认不能直接 `json.dumps`，要先 `isoformat()` 成字符串。

Windows 的官方 Python 常常不带 IANA 时区表，`ZoneInfo("Asia/Shanghai")` 会报 `ZoneInfoNotFoundError`。装一下即可：

```bash
python -m pip install tzdata
```

示例脚本在没装时会退回本地时区，不至于直接崩溃。

---

## 4. `collections.Counter`

```python
from collections import Counter

c = Counter(["java", "python", "java", "go", "java"])
print(c.most_common(2))   # [('java', 3), ('python', 1)]
```

对标「统计频次」，别手写 `dict[str, int]` 累加（能写，但 Counter 更短、带 `most_common`）。

---

## 5. pip 和 venv（第 05 课的落地）

```bash
source .venv/Scripts/activate          # Git Bash
python -m pip install requests         # 永远 python -m pip
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

| Maven | pip |
|---|---|
| `pom.xml` | `requirements.txt` 或 `pyproject.toml` |
| 坐标 `group:artifact:version` | 包名 + 版本 |
| 传递依赖较强 | 有，但锁定不如 Maven 严谨 |
| 不要改系统 JDK | 不要对系统 Python 裸装包 |

装之前问：标准库有没有？有就别装。

---

## 本课肌肉记忆

1. 先标准库，再 PyPI
2. 命令行用 `argparse`
3. 计时区用 `ZoneInfo`，JSON 里时间先变字符串
4. 计数用 `Counter`
5. `python -m pip` 装进当前 venv
6. `pip freeze` 能生成依赖清单，但严肃项目更常用 `pyproject.toml`

下一课用目前学过的东西做一个命令行待办，把模块、文件、JSON、异常、参数拼起来。
