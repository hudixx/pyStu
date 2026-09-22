# 第 20 课：从 MockMvc 看 TestClient

Spring 测 Controller 常用 MockMvc，不真开 8080。
FastAPI 用 `TestClient`：同样不监听端口，直接灌请求进应用。

本课示例去测第 18 课的 `18_app.py`。先激活 venv 并装过 `.[web,test]`。

```bash
cd 20-pytest测API
PYTHONUTF8=1 python -m pytest test_hello.py -v
```

`pytest` 发现 `test_*.py` 里以 `test_` 开头的函数，不必继承 `TestCase`。

---

## 1. TestClient ≈ MockMvc

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_hello() -> None:
    r = client.get("/hello", params={"name": "hudi"})
    assert r.status_code == 200
    assert r.json()["message"] == "你好, hudi"
```

| Spring | pytest + TestClient |
|---|---|
| `@SpringBootTest` + MockMvc | `TestClient(app)` |
| `get("/hello").param("name","hudi")` | `client.get("/hello", params={"name": "hudi"})` |
| `content().json(...)` | `r.json()` |
| `status().isOk()` | `assert r.status_code == 200` |
| `@AutoConfigureMockMvc` | 无需，Client 直接包 app |

POST JSON：`client.post("/hello", json={"name": "hudi"})`。

---

## 2. 和 unittest 的差别（第 10 课对照）

```python
# unittest
self.assertEqual(a, b)

# pytest
assert a == b
```

失败时 pytest 会把两边的值打出来，一般够用。
本课练习用 pytest，不要用 unittest。

测 404：

```python
r = client.post("/todos/99/done")
assert r.status_code == 404
```

---

## 3. 测带文件的 API 时

第 19 课接口会写 `todos.json`。测试里建议：

- 用临时文件，或
- 测完删除，或
- 把路径做成可注入（进阶，本课不强制）

示例测试第 18 课应用，它不写文件，最省事。

---

## 本课肌肉记忆

1. `TestClient(app)` 不占端口
2. pytest：文件 `test_*.py`，函数 `test_*`，普通 `assert`
3. `json=` 发 body，`params=` 发 query
4. 状态码和 body 都要断言
5. 阶段四到此结束：工程化 → HTTP → 校验 → 接口 → 测试

---

阶段四做完，你就具备：用 Python 写一个带校验、带测试的 JSON API，和写 Spring Controller 的心智已经对齐。
之后若要上数据库，再学 SQLAlchemy / 任意驱动；若要协程，再学 asyncio。
