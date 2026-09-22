# 第 17 课：从 Bean Validation 看 pydantic

Java 用 DTO + `@NotNull` / `@Size` + Jackson。
Python 用 **pydantic v2**：既是 DTO，又做校验，还能和 JSON 互转。FastAPI 的请求体就是它。

先激活 venv 并装过 `.[web]`。然后：

```bash
PYTHONUTF8=1 python 17-pydantic数据校验/17_pydantic.py
```

---

## 1. 一个模型 ≈ 带校验的 Java Record / DTO

```python
from pydantic import BaseModel, Field, ValidationError

class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    years: int = Field(ge=0, le=80)  # ge = greater or equal
```

```python
u = UserIn(name="hudi", years=30)     # 校验通过
print(u.name, u.years)
print(u.model_dump())                 # → dict，方便 json.dumps
print(u.model_dump_json())            # → JSON 字符串
```

非法数据：

```python
try:
    UserIn(name="", years=-1)
except ValidationError as e:
    print(e.errors())
```

| Java | pydantic |
|---|---|
| class + getter / record | `class UserIn(BaseModel)` |
| `@NotBlank` `@Size` | `Field(min_length=...)` |
| `@Min` `@Max` | `Field(ge=..., le=...)` |
| `@Email` | `EmailStr`（需额外 email-validator，本课不用） |
| Jackson 反序列化 | `UserIn.model_validate(dict)` / `model_validate_json` |
| 校验失败抛 `ConstraintViolation` | `ValidationError` |

类型注解就是契约：`years: int` 传入 `"30"` 时，pydantic **会尝试转换** 成 int。这点和 Jackson 类似，和「纯类型注解不检查」不同——**pydantic 在构造时真的跑校验**。

---

## 2. 嵌套和默认值

```python
class AccountIn(BaseModel):
    owner: str
    balance: int = 0          # 默认值，请求里可省略

class CreateOrder(BaseModel):
    user: UserIn
    note: str | None = None   # 可选
```

`model_dump()` 默认带 None。只要有值的字段：`model_dump(exclude_none=True)`。

---

## 3. 不要用 dict 当 API 边界

脚本内部用 dict 没问题。一旦数据来自请求、文件、命令行，就用 pydantic 模型接住。
否则你又会手写一堆 `if "name" not in data`——Java 里也不该拿 `Map<String,Object>` 当 Controller 入参。

---

## 本课肌肉记忆

1. DTO 用 `BaseModel`，校验写在 `Field(...)` 或类型上
2. 成功：`model_dump()` / `model_dump_json()`
3. 失败：抓 `ValidationError`
4. pydantic 会做类型转换，普通注解不会
5. FastAPI 下一课会自动用这些模型解析请求体

下一课 FastAPI：对标 Spring MVC。
