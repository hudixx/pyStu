"""第 19 课参考答案。

GET /todos、POST /todos、空 title 422、id = max+1，这些你都对。
两处必须改：
1. 标记完成题目是 POST /todos/{id}/done，你写成了 GET，所以按作业打会 405。
2. done 里改了内存里的 dict，没有 writes()，所以再 GET /todos 仍是 done=false。

对照题（命令行第 14 课 vs HTTP）：
能原样复用的：读文件、写文件、算下一个 id（Repository）。
要新写的：路由函数（Controller），以及入参 DTO。
业务「追加一条 / 标完成」可以共用，只是入口从 argparse 换成 FastAPI。
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="第 19 课练习")
DATA = Path(__file__).with_name("todos.json")


class TodoIn(BaseModel):
    """只收客户端该传的字段。id / done 由服务端填。"""

    title: str = Field(min_length=1)


def load_todos() -> list[dict]:
    """文件不存在当空列表。对照第 14 课 load_todos。"""
    if not DATA.exists():
        return []
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_todos(items: list[dict]) -> None:
    """覆盖写回。对照第 14 课 save_todos。"""
    DATA.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def next_id(items: list[dict]) -> int:
    """最大 id + 1，空列表从 1 开始。不要用 len+1。"""
    return max((item["id"] for item in items), default=0) + 1


@app.get("/todos")
def list_todos() -> list[dict]:
    return load_todos()


@app.post("/todos", status_code=201)
def add_todo(body: TodoIn) -> dict:
    items = load_todos()
    todo = {"id": next_id(items), "title": body.title, "done": False}
    items.append(todo)
    save_todos(items)
    return todo


@app.post("/todos/{todo_id}/done")
def mark_done(todo_id: int) -> dict:
    """path 参数 todo_id。改完必须 save，否则只改了内存。"""
    items = load_todos()
    for item in items:
        if item["id"] == todo_id:
            item["done"] = True
            save_todos(items)
            return item
    raise HTTPException(status_code=404, detail="找不到该待办")


if __name__ == "__main__":
    import uvicorn

    # 文件名以数字开头，不能写成 uvicorn 19_练习:app（模块名非法）。
    # 传 app 对象即可。reload 依赖 import 字符串，这里关掉。
    # 端口 8002，躲开第 18 课的 8000。
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
