import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union

class TodoIn(BaseModel):
    id: int = 1
    title: str = ""
    done: bool = False


api = FastAPI(title = "第18课练习")


@api.get("/ping")
def ping() -> dict[str, str]:
    return {"msg": "pong"}

@api.get("/repeat")
def repeat(text: str, times: int = 2) -> dict[str, str]:
    return {"result" : text * times}

@api.post("/pydantic_dto")
def pydantic_to(body: TodoIn) -> dict[str, Union[int, str, bool]]:

    return body.model_dump()

if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=8000,  reload=False)
    #     uvicorn.run("18_app:app", host="127.0.0.1", port=8000, reload=False)

"""
第四题，不知道，请在该注释下补充作答：

"""

