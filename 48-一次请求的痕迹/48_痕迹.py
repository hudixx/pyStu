"""第 48 课示例：一次请求留下能回放的字段。没有这些，线上只剩一句答错了的话。

对照 access log：时间、路径、状态码、耗时。这里多了检索出处、模型名、token。
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
# 第 26 课的假模型。本课只借它的 usage 字段，不改那个文件。
sys.path.insert(0, str(_ROOT / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "trace48_" + file_name.replace(".", "_")
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
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))


def trace_retrieval(question: str) -> dict:
    """检索路径。没打模型，模型名就写「未调用」，token 写 0。不要留空。"""
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
    """闲聊路径。token 从响应的 usage 抄，不自己估算后假装是账单。"""
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,
        max_retries=0,
    )
    started = time.perf_counter()
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好"}],
            temperature=0,
        )
    finally:
        await client.close()
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    usage = resp.usage
    return {
        "question": "你好",
        "sources": [],  # 这路没有检索。空列表和「未调用模型」不是同一栏。
        "model": "mock-chat",
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
        "latency_ms": elapsed_ms,
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
    show(trace_retrieval("公司地址在哪"))
    show(await trace_chat(base_url))


def main() -> None:
    import asyncio

    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
