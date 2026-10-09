"""第 37 课示例：POST /ask 返回答案和出处。不打聊天模型，不占端口。

对照：一个只读查询接口。资料在启动时切块、算向量，请求里只带问题。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

_ROOT = Path(__file__).resolve().parent.parent


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")

_HANDBOOK = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
# 进程启动时建一次索引。对照：应用启动加载缓存，不是每个请求读完整本手册再嵌入。
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))

app = FastAPI(title="第 37 课演示")


class AskIn(BaseModel):
    question: str = Field(min_length=1)


class AskOut(BaseModel):
    answer: str
    sources: list[str]


@app.post("/ask")
def ask(body: AskIn) -> AskOut:
    """普通 def：里面没有 await。检索是内存计算，不必写成 async。"""
    text, sources = _cite.answer(body.question, _INDEX)
    return AskOut(answer=text, sources=sources)


def main() -> None:
    client = TestClient(app)
    ok = client.post("/ask", json={"question": "退款几天"})
    print("/ask 退款", ok.status_code, ok.json())
    missing = client.post("/ask", json={"question": "公司地址在哪"})
    print("/ask 地址", missing.status_code, missing.json())


if __name__ == "__main__":
    main()
