"""第 37 课参考答案。题 1、题 2 都过。

题 1 的接口是对的：POST /ask，question 最短 1 个字符。
用「客服电话多少」打，状态码 200，sources 含「客服」，answer 里有 400-100-1000。
你 main 里打的是「退款几天」，不是题目那一问。结果碰巧也对，自测题目偏了。
空字符串会 422，函数体不会跑。这点和示例一致。

题 2 过。「公司地址在哪」仍是 200，「不知道」，sources 是 []。拒答不是 404。

变量名 model 能跑，但容易和「模型」混。加载出来的是模块，应叫 module。
json = {...} 这种关键字参数，等号两边不要空格。

题 3：
- 函数体里没有 await，就用普通 def。检索是内存里的计算，写成 async def 不会更快。
  FastAPI 会把同步路由丢进线程池，不堵住事件循环。
  对照第 24 课：async def 里如果塞进同步的阻塞调用，事件循环会被卡住。
  没有 await 却写成 async，只是看起来像异步。
- sources 为空，说明手册里没有这个事实。再去调模型「帮我想一个地址」，
  模型会编一个。调用方看到 200 和一个地址，分不出是查到的还是编的。
  空出处就是信号：这不是从手册查到的。拒答是正常业务结果。
  真要让模型改写，也只能接在 sources 非空之后。本课先不接。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI  # 应用对象。路由登记在它上面。对照 Spring 的应用上下文。
from fastapi.testclient import TestClient  # 进程内客户端，不 listen 端口。对照 MockMvc。
from pydantic import BaseModel, Field  # 请求体、响应体。构造时真校验。

_ROOT = Path(__file__).resolve().parent.parent  # 仓库根。手册不在本目录。


def _load(folder: str, file_name: str):
    """按路径加载前几课。文件名以数字开头，import 语句写不出来。"""
    path = _ROOT / folder / file_name
    module_name = "ans_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # 先登记，@dataclass 执行时才能按模块名找到自己。
    spec.loader.exec_module(module)
    return module


# 下面几行在加载本模块时就执行，不是等第一个请求。对照静态初始化块。
_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")

_HANDBOOK = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
# 进程启动时建一次索引。手册改了必须重启，这份 _INDEX 不会自己变。
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))

app = FastAPI(title="第 37 课参考答案")


class AskIn(BaseModel):
    """POST /ask 的请求体。缺字段、null、或空字符串，进路由之前就 422。"""

    question: str = Field(min_length=1)


class AskOut(BaseModel):
    """响应体。拒答时 answer 是「不知道」，sources 是空列表，不是 HTTP 错误。"""

    answer: str
    sources: list[str]


@app.post("/ask")
def ask(body: AskIn) -> AskOut:
    """普通 def：里面没有 await。对照 @PostMapping("/ask")。"""
    # 第 35 课已经决定拒答。这里不再判断，也不去调聊天模型补一个答案。
    text, sources = _cite.answer(body.question, _INDEX)
    return AskOut(answer=text, sources=sources)


def main() -> None:
    client = TestClient(app)
    # 题目要求的是客服电话，不是退款。
    ok = client.post("/ask", json={"question": "客服电话多少"})
    print("/ask 客服", ok.status_code, ok.json())
    missing = client.post("/ask", json={"question": "公司地址在哪"})
    print("/ask 地址", missing.status_code, missing.json())


if __name__ == "__main__":
    main()
