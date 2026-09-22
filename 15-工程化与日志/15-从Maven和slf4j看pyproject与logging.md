# 第 15 课：从 Maven 和 slf4j 看 pyproject 与 logging

阶段四开始。目标是把「会写脚本」升级成「能进工程」：依赖怎么声明、日志怎么打。
对照你熟悉的 `pom.xml` + `logback.xml` / slf4j。

运行示例：

```bash
PYTHONUTF8=1 python 15-工程化与日志/15_日志.py
```

本课起第三方包都装进项目根的 `.venv`，不要装到系统 Python。

---

## 1. `pyproject.toml` ≈ `pom.xml` 的现代写法

项目根已经放了 `pyproject.toml`。核心对照：

| Maven | Python |
|---|---|
| `groupId` / `artifactId` / `version` | `[project] name` / `version` |
| `<dependencies>` | `[project] dependencies` |
| `<optional>` / profile | `[project.optional-dependencies]` |
| `mvn -DskipTests` 之类 | extras：`pip install -e ".[web,test]"` |
| 编译进 target | 解释执行；`-e` 表示以可编辑方式安装本项目 |

```bash
source .venv/Scripts/activate
python -m pip install -e ".[web,test]"
```

装完应能 `python -c "import fastapi, httpx, pytest"`。
第 16–20 课都依赖这一步。没装的话后面 import 会 `ModuleNotFoundError`。

`requirements.txt` 仍然能用，相当于「冻住的依赖清单」。新项目优先 `pyproject.toml`。

---

## 2. `logging` ≈ slf4j + 一个默认 logback

不要再用 `print` 当日志。标准库 `logging` 就够日常用。

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)  # 类似 LoggerFactory.getLogger(Xxx.class)

logger.debug("调试，默认看不到")
logger.info("正常信息")
logger.warning("警告")
logger.error("出错")
```

| Java | Python |
|---|---|
| `LoggerFactory.getLogger(Foo.class)` | `logging.getLogger(__name__)` |
| `log.info("hi {}", name)` | `logger.info("hi %s", name)`（优先 %s，不要先 f-string 再传入，省掉不该组装的字符串） |
| `DEBUG/INFO/WARN/ERROR` | `DEBUG/INFO/WARNING/ERROR`（注意 WARNING 全称） |
| `logback.xml` | `basicConfig` 或 `dictConfig`；复杂项目才拆配置文件 |

`__name__` 在被 import 时是模块名，直接运行时是 `"__main__"`。按模块过滤日志时，这点有用。

级别：生产默认 INFO。想看 DEBUG：

```python
logging.basicConfig(level=logging.DEBUG)
```

多次 `basicConfig` 只有 **第一次** 生效。所以入口（`main`）里配一次，别的模块只 `getLogger`。

---

## 3. 日志往文件里写

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # 控制台
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)
```

Windows 上 `FileHandler` 同样要 `encoding="utf-8"`。

---

## 本课肌肉记忆

1. 依赖写进 `pyproject.toml`，用 `python -m pip install -e ".[web,test]"` 装进 venv
2. 日志用 `logging.getLogger(__name__)`，不要 `print`
3. `basicConfig` 只在入口调一次
4. `logger.info("a %s", x)` 用延迟格式化
5. `WARNING` 不是 `WARN`

下一课用 httpx 发 HTTP 请求，对标 `HttpClient` / OkHttp。
