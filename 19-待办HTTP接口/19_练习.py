
import json
from pathlib import Path
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

app = FastAPI(title = "19课练习")
todos = Path(__file__).with_name("todos.json")

class Todo(BaseModel):
    title: str = Field(min_length=1)
    id: int = 0
    done: bool = False

def reads() -> list[dict]:
    if todos.exists():
        return json.loads(todos.read_text(encoding="utf-8"))
    else:
        return []
def writes(indata: list[dict]) -> None:
    todos.write_text(
        json.dumps(indata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

@app.get("/todos")
def get_todos() -> list[dict]:
    return reads()

@app.post("/todos", status_code=201)
def in_todos(todo: Todo) -> Todo:
    todos_dict = reads()
    mid = max([x['id'] for x in todos_dict], default = 0) +1
    todo.id = mid
    todos_dict.append(todo.model_dump())
    writes(todos_dict)
    return todo

@app.post("/todos/{todo_id}/done")
def done(todo_id: int) -> dict:
    todos_dict = reads()
    for x in todos_dict:
        if x["id"] == todo_id:
            x["done"] = True
            writes(todos_dict)
            return x
    else:
        raise HTTPException(status_code=404, detail="找不到该待办")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("19_练习:app", host="127.0.0.1", port=8000, reload=True)

"""
对照题不知道，请在注释中给出简要答案
"""