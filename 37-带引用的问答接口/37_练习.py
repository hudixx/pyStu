import sys
from pathlib import Path
import importlib.util

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

_ROOT = Path(__file__).resolve().parent.parent

def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.split("_")[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    model = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = model
    spec.loader.exec_module(model)
    return model

_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")
_HANDBOOK = (_ROOT / "32-文档切块"/ "手册.md").read_text(encoding="utf-8")
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))

app = FastAPI(title= "37_练习")

class AskIn(BaseModel):
    question: str = Field(min_length=1)
class AskOut(BaseModel):
    answer: str
    sources: list[str]

@app.post("/ask")
def ask(body: AskIn) -> AskOut:
    text, sources = _cite.answer(body.question, _INDEX)
    return AskOut(answer=text, sources=sources)

def main() -> None:
    client = TestClient(app)
    ok = client.post("/ask", json = {"question": "退款几天"})
    print("/ask 退款",ok.status_code, ok.json())
    missing = client.post("/ask", json={"question": "公司地址在哪"})
    print("/ask 地址", missing.status_code, missing.json())

if __name__ == "__main__":
    main()

"""
    题3不知道，请在参考答案的注释中个给出
"""



