"""第 19 课示例：便签 API（不是待办）。作业请另写 19_练习.py。

对照 Spring Boot：
- pydantic 模型 ≈ DTO
- _load / _save ≈ Repository（这里用 JSON 文件当 DAO，不上数据库）
- 路由函数 ≈ Controller，里面调仓库
- 同一套 load/save，换 HTTP 当入口；第 14 课是命令行当入口

运行：

    cd 19-待办HTTP接口
    PYTHONUTF8=1 python 19_notes.py

- GET  http://127.0.0.1:8002/notes
- POST http://127.0.0.1:8002/notes  body: {"text": "hello"}
- DELETE http://127.0.0.1:8002/notes/{id}
- 文档 http://127.0.0.1:8002/docs
"""

from __future__ import annotations

# json：读写数组。对照 Jackson。
import json
# Path：文件路径。对照 java.nio.file.Path。
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 应用实例。端口在文件底部 uvicorn 里设成 8002，避免和第 18 课的 8000 抢。
app = FastAPI(title="便签演示")
# with_name("notes.json")：和本文件同目录的 notes.json，不依赖你从哪 cd。
# 对照 Paths.get("notes.json") 但绑在 class 文件旁边，而不是进程工作目录。
DATA = Path(__file__).with_name("notes.json")


class NoteIn(BaseModel):
    """创建便签的入参。只有 text，没有 id（id 由服务端分配）。

    对照只含业务字段的 CreateXxxRequest。空字符串 min_length=1 会 422。
    """

    text: str = Field(min_length=1, max_length=200)


class Note(NoteIn):
    """完整便签 = 入参字段 + id。继承 NoteIn 就不用把 text 再写一遍。

    对照：CreateRequest 和 带 id 的实体分两个类，实体多一个 id。
    本课路由返回的是 dict，这个类主要给阅读用，也方便以后改成 response_model=Note。
    """

    id: int


def _load() -> list[dict]:
    """读文件 → list[dict]。文件不存在当空列表，不要抛。

    下划线开头：约定「模块内部用」，对照 private。Python 不会强制拦住外部调用。
    """
    if not DATA.exists():
        return []  # 第一次还没 POST 过，没有文件是正常的
    # read_text 一次读成 str；json.loads 再变成 list。encoding 必须 utf-8，否则中文会乱。
    return json.loads(DATA.read_text(encoding="utf-8"))


def _save(items: list[dict]) -> None:
    """list[dict] → 写回文件。覆盖写，不追加。

    ensure_ascii=False：中文原样写入，不要 \uXXXX。
    indent=2：带缩进，方便你用编辑器打开看。
    """
    DATA.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.get("/notes")
def list_notes() -> list[dict]:
    """列出全部便签。对照 GET 集合资源，直接 return 列表即可。"""
    return _load()


@app.post("/notes", status_code=201)
def add_note(body: NoteIn) -> dict:
    """新建一条。201 Created 对照 @ResponseStatus(CREATED)。

    body 已经通过 pydantic：text 非空、不超过 200 字。
    """
    items = _load()
    # 生成 id：现有最大 id + 1；空列表时 default=0，于是第一条是 1。
    # 不要用 len(items)+1：中间删过就会和旧 id 撞。对照第 14 课踩过的坑。
    # 生成器表达式 (x["id"] for x in items) 惰性取每个 id，max 只关心最大值。
    new_id = max((x["id"] for x in items), default=0) + 1
    # 响应和落盘都用 dict，和 JSON 文件结构一致：{"id": 1, "text": "..."}。
    note = {"id": new_id, "text": body.text}
    items.append(note)  # 追加到内存列表，还没写盘
    _save(items)  # 写盘。进程一关数据还在，因为在文件里。
    return note  # 把新建那条返回给客户端，方便立刻拿到 id


@app.delete("/notes/{note_id}")
def delete_note(note_id: int) -> dict[str, bool]:
    """按 id 删除。找不到 404。对照 @DeleteMapping("/notes/{id}")。"""
    items = _load()
    # 列表推导：留下 id 不等于 note_id 的。等于过滤掉目标那条。
    # 对照 items.removeIf(x -> x.getId().equals(noteId))。
    kept = [x for x in items if x["id"] != note_id]
    # 长度没变 = 没有任何一条被滤掉 = id 不存在。
    if len(kept) == len(items):
        raise HTTPException(status_code=404, detail="找不到便签")
    _save(kept)  # 把滤完的列表写回，等于删除
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    # 端口 8002，躲开第 18 课的 8000。模块名 19_notes 对应本文件。
    uvicorn.run("19_notes:app", host="127.0.0.1", port=8002, reload=False)
