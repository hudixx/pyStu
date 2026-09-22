# 第 18 课：从 Spring MVC 看 FastAPI

FastAPI 对标 Spring Web（偏注解风格的那一种）：用类型注解声明参数，自动生成 OpenAPI 文档，请求体走 pydantic。

先激活 venv 并装过 `.[web]`。

运行示例有两种方式。

**A. 当脚本跑（适合看一眼）：**

```bash
cd 18-FastAPI入门
PYTHONUTF8=1 python 18_app.py
```

然后浏览器打开 http://127.0.0.1:8000/hello?name=hudi  
文档：http://127.0.0.1:8000/docs  
停掉：终端 Ctrl+C

**B. 用 uvicorn（更接近生产）：**

```bash
cd 18-FastAPI入门
python -m uvicorn 18_app:app --reload --port 8000
```

必须先 `cd` 进本目录：文件夹名带连字符，不能当 Python 包 import。

---

## 1. 对照表

| Spring | FastAPI |
|---|---|
| `@RestController` | `app = FastAPI()` |
| `@GetMapping("/hello")` | `@app.get("/hello")` |
| `@RequestParam String name` | 函数参数 `name: str` |
| `@RequestBody UserIn dto` | 参数类型 `user: UserIn`（pydantic） |
| `@PathVariable Long id` | `id: int` 出现在路径 `{id}` |
| `ResponseEntity` | 直接 return dict / BaseModel；或 `JSONResponse` |
| `application.yml` 端口 | uvicorn `--port` |
| springdoc / swagger | 自带 `/docs` |

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello(name: str = "陌生人") -> dict[str, str]:
    return {"message": f"你好, {name}"}
```

函数里的 `name: str` 自动变成 query 参数 `?name=`。
路径里写了 `{item_id}`，同名参数就是 path variable。

POST + body：

```python
from pydantic import BaseModel

class HelloIn(BaseModel):
    name: str

@app.post("/hello")
def hello_post(body: HelloIn) -> dict[str, str]:
    return {"message": f"你好, {body.name}"}
```

一个 pydantic 参数、没有放进路径，FastAPI 就当 JSON body。这和 `@RequestBody` 一样自然。

---

## 2. 错误和状态码

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, str]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="非法 id")
    return {"id": str(user_id)}
```

校验失败（pydantic）自动 422，不必自己写。这比 Spring 默认还省事。

---

## 3. 同步函数就可以

本课用普通 `def`，不要 `async def`。IO 少的接口这样最简单。
`async def` 对标 WebFlux / 协程，阶段四先不碰。

---

## 本课肌肉记忆

1. `cd` 进目录再起 uvicorn，因为目录名不能当包
2. query / path / body 靠「参数怎么声明」区分，很少写注解堆
3. 返回 dict 或 BaseModel 即可，不必 `ResponseEntity.ok()`
4. `/docs` 自带 Swagger
5. 业务错误 `raise HTTPException`

下一课把第 14 课待办做成 HTTP 接口。
