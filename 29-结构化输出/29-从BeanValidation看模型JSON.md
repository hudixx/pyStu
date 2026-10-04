# 第 29 课：从 Bean Validation 看模型 JSON

你要的是 `{"name": "hudi", "score": 70}` 这种结构，不是散文。模型仍可能：

- 包一层 markdown 代码块
- 漏字段
- 把 `score` 写成字符串
- 直接胡言乱语

**模型输出不可信**，和不可信的 `@RequestBody` 一样：用 pydantic 接，失败就失败，不要 `json.loads` 之后当成功。

运行：

```bash
PYTHONUTF8=1 python 29-结构化输出/29_json.py
```

会先成功解析一条，再故意打 `TRIGGER:BADJSON`，抓住校验/解析错误。

---

## 1. 请求侧：请模型吐 JSON

兼容面最广的写法（多数国产网关都认）：

```python
resp = await client.chat.completions.create(
    model="mock-chat",
    messages=[
        {"role": "system", "content": "只返回 JSON，不要 markdown。"},
        {"role": "user", "content": "抽取姓名和分数"},
    ],
    response_format={"type": "json_object"},
    temperature=0,
)
raw = resp.choices[0].message.content or ""
```

OpenAI 自家还有 `client.chat.completions.parse(..., response_format=YourModel)`，部分兼容网关 **没有**。岗位代码优先 `json_object` + 自己校验，能用 parse 再开。

假模型：带上 `json_object` 就返回 `{"name": "hudi", "score": 70}`。

---

## 2. 响应侧：pydantic（第 17 课）

```python
from pydantic import BaseModel, Field, ValidationError

class Person(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)

person = Person.model_validate_json(raw)
```

| 情况 | 结果 |
|---|---|
| 合法 JSON 且字段对 | 得到 `Person` |
| 根本不是 JSON | `ValidationError` / `json.JSONDecodeError` |
| JSON 有了但缺字段、类型不对 | `ValidationError` |

对照：`ObjectMapper.readValue` + `@NotNull`。Jackson 也能读脏 JSON 成 `Map` 然后 NPE；你现在直接挡在边界。

不要：

```python
data = json.loads(raw)
return data["name"]   # 缺键就炸在业务里，还没有 422
```

---

## 3. 假模型的坏例子

user 消息含 `TRIGGER:BADJSON` 时，假模型返回 `{name: hudi, score: 70`（缺引号）。
练习里必须让这条路径 **失败**，不能 catch 之后返回默认值假装成功。

---

## 本课肌肉记忆

1. 要结构就 `response_format=json_object` + 低温
2. 用 `model_validate_json`，不要只 `json.loads`
3. 失败要暴露，不要默默填默认
4. `.parse()` 是锦上添花，不是兼容网关的前提

下一课：超时、429、重试。模型网关比你们内网 RPC 更容易抽风。
