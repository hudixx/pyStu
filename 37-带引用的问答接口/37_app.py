"""第 37 课示例：POST /ask 返回答案和出处。不打聊天模型，不占端口。

对照：一个只读查询接口。资料在启动时切块、算向量，请求里只带问题。
直接 python 本文件时用 TestClient 在进程内打自己，对照 MockMvc，不必先 uvicorn。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI  # 应用对象。路由用装饰器登记到它上面。对照 Spring 的应用上下文，这里就是一个普通对象。
from fastapi.testclient import TestClient  # 进程内客户端，不 listen 端口。对照 MockMvc。
from pydantic import BaseModel, Field  # 请求体、响应体。构造时真校验。对照 Jackson + Bean Validation。

_ROOT = Path(__file__).resolve().parent.parent  # 仓库根。手册和前几课都不在本目录。


def _load(folder: str, file_name: str):
    """按路径加载前几课。文件名以数字开头，import 语句写不出来。"""
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # 先登记，@dataclass 执行时才能按模块名找到自己。
    spec.loader.exec_module(module)
    return module


# 下面几行在「加载本模块」时就执行，不是等第一个请求。对照静态初始化块。
_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")

_HANDBOOK = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
# 进程启动时建一次索引。对照：应用启动加载缓存，不是每个请求读完整本手册再嵌入。
# 手册改了必须重启进程，这份 _INDEX 不会自己变。本课的手册是只读示例，这样够用。
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))

app = FastAPI(title="第 37 课演示")  # title 会出现在自动生成的 /docs 页面上。


class AskIn(BaseModel):
    """POST /ask 的请求体。JSON 字段名就是 question。对照一个只有一个字段的 @RequestBody。"""

    question: str = Field(min_length=1)  # 缺字段、null、或 ""，进路由函数之前就 422。函数体不会跑。


class AskOut(BaseModel):
    """响应体。FastAPI 看到返回类型是 BaseModel，会把它序列化成 JSON。对照 @RestController 返回 DTO。"""

    answer: str  # 回答正文。拒答时是「不知道」，不是 HTTP 错误。
    sources: list[str]  # 出处。拒答时是空列表 []，JSON 里就是 "sources": []。


@app.post("/ask")
def ask(body: AskIn) -> AskOut:
    """普通 def：里面没有 await。检索是内存计算，不必写成 async。

    @app.post 把这个函数登记成 POST /ask。对照 @PostMapping("/ask")。
    body 由 FastAPI 按 AskIn 解析并校验，不用自己读输入流。
    同步路由会被 FastAPI 丢进线程池，避免堵住事件循环。本课没有别的并发请求，知道有这回事即可。
    """
    # _cite.answer 来自第 35 课：不够像就返回「不知道」和空出处，这里不再判断一次。
    text, sources = _cite.answer(body.question, _INDEX)
    # 构造响应对象。字段名是关键字参数。return 它，不要 return 一个 dict，类型才和 -> AskOut 一致。
    return AskOut(answer=text, sources=sources)


def main() -> None:
    # 不占端口。请求在进程里直接进 app。对照 MockMvcBuilders.standaloneSetup。
    client = TestClient(app)
    # json= 会序列化成请求体并带上 Content-Type: application/json。对照 post(...).contentType(JSON).content(...)。
    ok = client.post("/ask", json={"question": "退款几天"})
    # status_code 是 int。json() 把响应体解析成 dict。对照 response.getStatus() 再 readTree。
    print("/ask 退款", ok.status_code, ok.json())
    missing = client.post("/ask", json={"question": "公司地址在哪"})
    # 这题手册里没有。预期仍是 200，正文是「不知道」，sources 是空列表。拒答不是 404。
    print("/ask 地址", missing.status_code, missing.json())


if __name__ == "__main__":
    # TestClient 会自己处理这个同步接口。这里没有 async def，不需要 asyncio.run。
    main()
