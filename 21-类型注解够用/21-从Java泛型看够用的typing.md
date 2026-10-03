# 第 21 课：从 Java 泛型看够用的 typing

阶段五开始。目标不是成为类型系统律师，而是 **能读官方 SDK 的函数签名，并写出 IDE / 检查器能看懂的注解**。

第 10 课讲过：注解运行时默认不检查。本课补的是 SDK 里最常见的四种写法：`list[str]`、`Literal`、`TypedDict`、`Protocol`。

描述符、`TypeVar` 体操、协方差全部不做。那是选修 B1。

运行示例：

```bash
PYTHONUTF8=1 python 21-类型注解够用/21_typing.py
```

---

## 1. 你已经会的

```python
def greet(name: str | None) -> str: ...
def ids() -> list[int]: ...
def ages() -> dict[str, int]: ...
```

| 含义 | Python | Java |
|---|---|---|
| 可空 | `str \| None` | `@Nullable String` |
| 列表 | `list[str]` | `List<String>` |
| 字典 | `dict[str, int]` | `Map<String, Integer>` |
| 任意 | `object` / `Any` | `Object`（`Any` 等于放弃检查） |

`Optional[str]` 和 `str | None` 一样，新代码用 `|`。

记住：`add("a", "b")` 注解写成 `int` 也能跑。拦错靠 IDE、mypy、pyright，不靠解释器。pydantic（第 17 课）是另一条路：**构造时真的校验**。

---

## 2. `Literal`：只允许这几个值

模型 API 里满是这种字段：`role` 只能是 `"system"` / `"user"` / `"assistant"`。

```python
from typing import Literal

Role = Literal["system", "user", "assistant"]

def say(role: Role, content: str) -> None:
    ...
```

| Java | Python |
|---|---|
| `enum Role { SYSTEM, USER }` | `Literal["system", "user"]`（运行时仍是普通 str） |
| `@StringDef` | 同上，给检查器看 |
| `"USER"` 魔法字符串满天飞 | 写成 Literal，拼错时 IDE 会划线 |

它 **不会** 在运行时拦住 `"admin"`。要运行时拦住，用 `Enum` 或 pydantic。Literal 的价值是读代码和补全。

---

## 3. `TypedDict`：已知字段的 dict

HTTP JSON 进 Python 往往是 `dict`，不是一个类。你又希望 `msg["role"]` 能补全。用 TypedDict：

```python
from typing import Literal, NotRequired, TypedDict

class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str
    name: NotRequired[str]   # 可以没有这个键
```

```python
msg: ChatMessage = {"role": "user", "content": "你好"}
```

| Java | Python |
|---|---|
| 一个 DTO / record | `TypedDict`（仍是 dict，没有 `.role` 属性） |
| `Map<String, Object>` 口头约定键 | 不写 TypedDict 时就是这样 |
| Jackson 反序列化到类 | 运行时还是 dict；检查器按键检查 |

取值仍是 `msg["content"]`，不是 `msg.content`。要属性访问和运行时校验，用第 17 课的 pydantic。

分工口诀：

- 只是 dict、想让 IDE 帮忙 → `TypedDict`
- 进接口边界、要真校验 → pydantic `BaseModel`
- 有方法的对象 → `Protocol`（第 07 课）

---

## 4. `Protocol` 再钉一次

第 07 课：只要有这个方法就算数，不必 `implements`。

```python
from typing import Protocol

class Closable(Protocol):
    def close(self) -> None: ...

def shutdown(resource: Closable) -> None:
    resource.close()
```

文件对象、httpx.Client、自己的连接，都能传。运行时不强制继承 `Closable`。

和 TypedDict 别混：Protocol 描述 **对象的方法**；TypedDict 描述 **字典的键**。

---

## 5. `type` 别名（3.12+，你是 3.13）

```python
type UserId = int
type Headers = dict[str, str]
```

给检查器看的别名，运行时 `UserId` 就是 `int`。不要为了装而把每个 `int` 都起名；只在「这个 int 其实是用户 id」这种容易混的地方用。

老写法 `UserId: TypeAlias = int` 也能遇到。

---

## 本课肌肉记忆

1. 注解默认不在运行时检查；pydantic 才检查
2. `Literal` 限制取值集合，给人和 IDE 看
3. JSON 形状用 `TypedDict`；取值仍是 `d["k"]`
4. 有方法的鸭子用 `Protocol`
5. 先别碰 `TypeVar` / 描述符

下一课 `async def` / `await`：对标 WebFlux，但先在脚本里跑，不动 FastAPI。
