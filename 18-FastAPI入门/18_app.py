"""第 18 课示例：最小 FastAPI 应用。

对照 Spring MVC：
- app = FastAPI() ≈ @RestController + 一个 Spring Boot 应用
- @app.get / @app.post ≈ @GetMapping / @PostMapping
- 函数参数 name: str ≈ @RequestParam
- 路径 {user_id} + 同名参数 ≈ @PathVariable
- 参数类型是 BaseModel ≈ @RequestBody
- raise HTTPException ≈ 抛 ResponseStatusException / 自己 setStatus
- /docs 自带 Swagger，对照 springdoc

运行（必须先 cd 进本目录，目录名带连字符不能当包）：

    cd 18-FastAPI入门
    PYTHONUTF8=1 python 18_app.py

浏览器：
    http://127.0.0.1:8000/hello?name=hudi
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

# FastAPI：Web 框架。HTTPException：业务错误时抛，框架转成对应状态码的 JSON。
from fastapi import FastAPI, HTTPException
# BaseModel / Field：第 17 课的 DTO。FastAPI 用它解析 JSON body 并做校验。
from pydantic import BaseModel, Field

# 创建一个应用实例。对照 @SpringBootApplication + @RestController 绑在一起。
# title 会出现在 /docs 页面标题上，不影响路由。
app = FastAPI(title="第 18 课演示")


class HelloIn(BaseModel):
    """POST /hello 的请求体。对照 @RequestBody 的 DTO。

    FastAPI 看到参数类型是 BaseModel、又没出现在路径里，就当 JSON body。
    空字符串会 422（Unprocessable Entity），不用自己写 if。
    """

    name: str = Field(min_length=1, max_length=20)


@app.get("/hello")
def hello(name: str = "陌生人") -> dict[str, str]:
    """query 参数：/hello?name=hudi

    name 没出现在路径 { } 里，FastAPI 就当 ?name=。
    默认值 "陌生人"：调用方不传时用它。对照 @RequestParam(defaultValue="陌生人")。
    返回 dict 即可，框架自动 JSON 序列化。不必 ResponseEntity.ok()。
    本课用普通 def，不要 async def（那是 WebFlux / 协程，后面再说）。
    """
    return {"message": f"你好, {name}"}


@app.post("/hello")
def hello_post(body: HelloIn) -> dict[str, str]:
    """JSON body：{"name": "hudi"}

    body: HelloIn → 从请求体反序列化并校验。对照 @RequestBody @Valid HelloIn body。
    校验失败自动 422，成功才能进函数。body.name 已经是通过校验的 str。
    """
    return {"message": f"你好, {body.name}"}


@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, int | str]:
    """路径参数。{user_id} 和函数参数同名，对照 @PathVariable int userId。

    类型写成 int：路径里是 /users/abc 会 422，框架先转类型再进函数。
    dict[str, int | str] 表示值可能是 int 或 str（id 是数字，name 是字符串）。
    """
    if user_id <= 0:
        # 业务非法：raise 后函数结束，FastAPI 回 {"detail": "非法 id"}，状态码 400。
        # 对照 throw new ResponseStatusException(BAD_REQUEST, "非法 id")。
        raise HTTPException(status_code=400, detail="非法 id")
    # f"user-{user_id}"：把 id 嵌进名字，演示用，不是查数据库。
    return {"id": user_id, "name": f"user-{user_id}"}


if __name__ == "__main__":
    # uvicorn 是 ASGI 服务器，对照内嵌 Tomcat。只在直接 python 本文件时才 import，避免测试里再起端口。
    import uvicorn

    # "18_app:app"：模块名:变量名，找到上面的 app 对象。
    # host 127.0.0.1 只本机可访问；port 8000 对照 server.port。
    # reload=False：改代码不会自动重启。开发时命令行可加 --reload。
    uvicorn.run("18_app:app", host="127.0.0.1", port=8000, reload=False)
