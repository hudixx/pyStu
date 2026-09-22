"""第 18 课示例：最小 FastAPI 应用。

    cd 18-FastAPI入门
    PYTHONUTF8=1 python 18_app.py

浏览器：
    http://127.0.0.1:8000/hello?name=hudi
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="第 18 课演示")


class HelloIn(BaseModel):
    name: str = Field(min_length=1, max_length=20)


@app.get("/hello")
def hello(name: str = "陌生人") -> dict[str, str]:
    """query 参数：/hello?name=hudi"""
    return {"message": f"你好, {name}"}


@app.post("/hello")
def hello_post(body: HelloIn) -> dict[str, str]:
    """JSON body：{"name": "hudi"}"""
    return {"message": f"你好, {body.name}"}


@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, int | str]:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="非法 id")
    return {"id": user_id, "name": f"user-{user_id}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("18_app:app", host="127.0.0.1", port=8000, reload=False)
