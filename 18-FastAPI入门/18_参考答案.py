"""第 18 课参考答案。

题 1 / 2 对：GET /ping、/repeat?text=go&times=3、times 默认 2。
题 3 成功路径也对，但 title 写成了默认 ""、没有 min_length=1，
所以 POST {"title":""} 和 POST {} 都是 200，题目要最短 1 个字符（应 422）。
变量名请用 app（练习里的 uvicorn 18_练习:app 靠这个名字）。
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

# 必须叫 app：python -m uvicorn 18_练习:app 里冒号后面就是这个变量名。
# 对照 Spring Boot 里 @SpringBootApplication 那个启动类被约定好怎么找。
app = FastAPI(title="第 18 课练习")


class TodoIn(BaseModel):
    """只描述请求体。id / done 是服务端填的，不要放进入参。

    title 没有默认值 → JSON 里缺 title 会 422。
    Field(min_length=1) → title="" 也会 422。对照 @NotBlank。
    """

    title: str = Field(min_length=1)


@app.get("/ping")
def ping() -> dict[str, str]:
    """无参数：路径就是 /ping。对照 @GetMapping("/ping")。"""
    return {"msg": "pong"}


@app.get("/repeat")
def repeat(text: str, times: int = 2) -> dict[str, str]:
    """text、times 不在路径 { } 里，又是 int/str，FastAPI 当 query。
    对照 @RequestParam String text, @RequestParam(defaultValue="2") int times。
    """
    return {"result": text * times}


@app.post("/todos")
def create_todo(body: TodoIn) -> dict[str, int | str | bool]:
    """body: TodoIn 且不在路径里 → JSON body。对照 @RequestBody @Valid TodoIn。
    校验过了才能进函数。id 写死 1，本课不落盘。
    """
    return {"id": 1, "title": body.title, "done": False}


# 题 4：FastAPI 怎么区分 query / path / body？对应 Spring 哪三个注解？
#
# 看「参数出现在哪、类型是什么」，很少再堆注解：
# - 名字出现在路径 {todo_id} 里     → path    ≈ @PathVariable
# - 不在路径里，类型是 str/int/bool → query   ≈ @RequestParam
# - 不在路径里，类型是 BaseModel    → body    ≈ @RequestBody
# 本文件：text/times 是 query；body 是 body。第 18_app.py 的 user_id 才是 path。


if __name__ == "__main__":
    import uvicorn

    # 端口 8001，躲开示例 18_app.py 的 8000。
    uvicorn.run("18_参考答案:app", host="127.0.0.1", port=8001, reload=False)
