"""第 48 课示例：一次请求留下能回放的字段。没有这些，线上只剩一句答错了的话。

对照 access log：时间、路径、状态码、耗时。这里多了检索出处、模型名、token。
每条痕迹是一个 dict，不是类。对照 Map<String, Object>。字段名靠约定，写错键要到打印时才发现。
"""

from __future__ import annotations

import importlib.util  # 加载 32、34、35 课。文件名以数字开头，不能用 import 语句。
import os  # 读 OPENAI_API_KEY。假模型不校验，没有就用占位。
import sys
import time  # perf_counter：测耗时。对照 System.nanoTime，不是 currentTimeMillis。
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # 仓库根。本文件在「48-一次请求的痕迹/」。
# 第 26 课的假模型。本课只借它的 usage 字段，不改那个文件。
# 目录名有连字符、还以数字开头，不能当包。把目录放进搜索路径，下面才能 import mock_llm。
sys.path.insert(0, str(_ROOT / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock  # 必须写在 sys.path.insert 之后。写在前面会找不到这个模块。


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


# 下面几行在 import 本文件时就执行。对照静态初始化：启动时切块、算向量，不是每个请求重做。
_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_cite = _load("35-引用与拒答", "35_引用.py")
_HANDBOOK = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
_INDEX = _search.build_index(_chunks.chunk_markdown(_HANDBOOK))


def trace_retrieval(question: str) -> dict:
    """检索路径。没打模型，模型名就写「未调用」，token 写 0。不要留空。

    空字符串和缺这个键不是一回事。回放时要能看出「这栏我们填了，值是零」，而不是「忘了记」。
    """
    started = time.perf_counter()  # 秒，float，从某个固定点算起。只和自己相减，不要拿去对墙钟。
    text, sources = _cite.answer(question, _INDEX)  # 第 35 课：不够像就「不知道」和空出处。不打模型。
    # 相减得到秒，乘 1000 变毫秒，int 丢掉小数。对照 (int) ((nanoTime 差) / 1_000_000)。
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
    """闲聊路径。token 从响应的 usage 抄，不自己估算后假装是账单。

    async def：里面有 await。调用它得到协程，要交给 asyncio.run。对照还没完成的 CompletableFuture。
    """
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 没有环境变量就用占位。真密钥不要写进源码。
        base_url=base_url,  # 本次 start_mock 分配的 http://127.0.0.1:端口/v1。
        timeout=1000.0,  # 单次 HTTP 的掐断，单位秒。和下面自己量的 latency_ms 不是同一个数。
        max_retries=0,
    )
    started = time.perf_counter()
    try:
        resp = await client.chat.completions.create(
            model="mock-chat",  # 这个名字会写进痕迹。假模型不看它，但日志里要能对上「打的是哪一个」。
            messages=[{"role": "user", "content": "你好"}],
            temperature=0,
        )
    finally:
        # 成功或抛异常都关连接池。耗时算在 finally 之后，所以关掉客户端的时间也算进 latency_ms。
        await client.close()
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    usage = resp.usage  # 有的网关不返回 usage，这时是 None。不能直接点 .prompt_tokens。
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
    """按固定栏位打印一条痕迹。键名写错会 KeyError，对照 map.get 拿到 null 再拆箱。"""
    print("问:", trace["question"])
    print("  出处:", trace["sources"])
    print("  模型:", trace["model"])
    print("  token:", trace["prompt_tokens"], "+", trace["completion_tokens"])
    print("  耗时ms:", trace["latency_ms"])
    print("  回答:", trace["answer"])


async def main_async(base_url: str) -> None:
    """先两条检索，再一条闲聊。检索不需要 base_url，闲聊需要。"""
    show(trace_retrieval("退款几天"))  # 同步函数，没有 await。出处应是「退款」。
    show(trace_retrieval("公司地址在哪"))  # 手册里没有。出处应是空列表，模型名仍是「未调用」。
    show(await trace_chat(base_url))  # await 等到那条闲聊痕迹的 dict，再交给同一个 show。


def main() -> None:
    # import 写在函数里：只有直接运行本文件、真要 asyncio.run 时才加载。
    # Java 的 import 必须在文件顶部，不能挪进方法。Python 可以。
    # async / await 是语法，不依赖这个 import。缺的是 asyncio.run 这个函数。
    import asyncio

    server, base_url = start_mock()  # 后台起第 26 课的假模型。元组拆包。
    try:
        asyncio.run(main_async(base_url))  # 新建事件循环，跑完协程，再关掉循环。
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
