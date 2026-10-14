"""第 48 课参考答案。题 1、题 2 都过。

退款几天：出处 ['退款']，模型是「未调用」，token 是 0 + 0。
公司地址：出处 []，回答是「不知道」。
你好：模型 mock-chat，prompt_tokens 是 2，从 resp.usage 读的，不是写死的。

地址题写成了「公司地址在哪儿」，多了一个「儿」。手册里没有地址，所以仍是拒答。
题目写的是「公司地址在哪」。换一种问法时，检索分数可能变，不要靠这次碰巧。

假模型的回声后面还有 temperature=0。那是第 26 课 mock_llm 把温度拼进回复，不是这课写错。

题 3：
- 只有最终回答时，看不出是检索空了、检索到了别的节，还是根本没打模型、打错了模型。
  出处、模型名、token、耗时就是用来分开这几件事的。
- 检索路径的 token 写 0，表示这栏记过了，值是零。把键省掉，回放时分不清「没调用」和「日志漏了这栏」。
  空的出处写成 []，也是这个原因。
"""

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
    path = _ROOT / folder / file_name
    module_name = "ans48_" + file_name.replace(".", "_")
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
    """没打模型也要把模型和 token 两栏填上。0 和缺键不是一回事。"""
    started = time.perf_counter()
    text, sources = _cite.answer(question, _INDEX)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {
        "question": question,
        "sources": sources,
        "model": "未调用",
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "latency_ms": elapsed_ms,
        "answer": text,
    }


async def trace_chat(base_url: str) -> dict:
    """token 只从 usage 抄。网关没给 usage 时记 0，不自己估。"""
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
        "sources": [],
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
    server, base_url = start_mock()
    try:
        asyncio.run(main_async(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
