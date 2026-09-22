"""第 19 课示例：便签 API（不是待办）。作业请另写 19_练习.py。

    cd 19-待办HTTP接口
    PYTHONUTF8=1 python 19_notes.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="便签演示")
DATA = Path(__file__).with_name("notes.json")


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class Note(NoteIn):
    id: int


def _load() -> list[dict]:
    if not DATA.exists():
        return []
    return json.loads(DATA.read_text(encoding="utf-8"))


def _save(items: list[dict]) -> None:
    DATA.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.get("/notes")
def list_notes() -> list[dict]:
    return _load()


@app.post("/notes", status_code=201)
def add_note(body: NoteIn) -> dict:
    items = _load()
    new_id = max((x["id"] for x in items), default=0) + 1
    note = {"id": new_id, "text": body.text}
    items.append(note)
    _save(items)
    return note


@app.delete("/notes/{note_id}")
def delete_note(note_id: int) -> dict[str, bool]:
    items = _load()
    kept = [x for x in items if x["id"] != note_id]
    if len(kept) == len(items):
        raise HTTPException(status_code=404, detail="找不到便签")
    _save(kept)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("19_notes:app", host="127.0.0.1", port=8002, reload=False)
