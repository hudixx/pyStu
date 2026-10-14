from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from pathlib import Path
from openai import AsyncOpenAI

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "26-模型SDK入门"))

from mock_llm import start_mock

def _load(folder: str, file_name: str):
    """按路径加载阶段七的课。返回模块对象，上面有 chunk_markdown、answer 这些函数。"""
    path = _ROOT / folder / file_name
    module_name = "trace48_" + file_name.replace(".", "_")  # 前缀和别的课分开，避免模块名撞车。
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # 先登记。被加载文件里的 @dataclass 要按模块名找到自己。
    spec.loader.exec_module(module)
    return module

_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")
_HANDBOOK = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))

def trace_retrieval(question: str) -> dict:
    started = time.perf_counter()
    text, sources = _cite.answer(question, _INDEX)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {
        "question": question,
        "sources": sources,  # 空列表表示拒答，不是「忘了记」。
        "model": "未调用",
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "latency_ms": elapsed_ms,
        "answer": text,
    }

async def trace_chat(base_url: str) -> dict:
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10,
        max_retries=0
    )
    started = time.perf_counter()
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好"}],
            temperature=0
        )
    finally:
        await client.close()
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    usage = resp.usage
    return {
        "question": "你好",
        "sources": [],  # 这路没有检索。空列表和「未调用模型」不是同一栏。
        "model": "mock-chat",
        # 三元表达式：usage 不是 None 才取字段，否则记 0。对照 usage == null ? 0 : usage.promptTokens。
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
        "latency_ms": elapsed_ms,
        # content 可能是 None。这里原样放进字典，不改成空串。打印时会看到 None。
        "answer": resp.choices[0].message.content,
    }

def show(trace: dict) -> None:
    print("问:", trace["question"])
    print("  出处:", trace["sources"])
    print("  模型:", trace["model"])
    print("  token:", trace["prompt_tokens"], "+", trace["completion_tokens"])
    print("  耗时ms:", trace["latency_ms"])
    print("  回答:", trace["answer"])

async def main_async(base_url: str) -> None:
    show(trace_retrieval("退款几天"))
    show(trace_retrieval("公司地址在哪儿"))
    show(await trace_chat(base_url))

def main() -> None:
    server, base_url = start_mock()  # 后台起第 26 课的假模型。元组拆包。
    try:
        asyncio.run(main_async(base_url))  # 新建事件循环，跑完协程，再关掉循环。
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""