"""第 34 课示例：内存里的 Top-K。生产以后可以换成 pgvector，查询形状一样。

本课不上数据库。阶段十才学 SQLAlchemy，现在装 Postgres 会挡住 RAG。
业务上的用户表、订单表以后仍是普通 SQL。向量只存「这块文字的坐标」。
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _load(file_name: str, folder: str):
    """文件名以数字开头，不能写 import 32_切块。对照第 20 课的 importlib。"""
    path = _ROOT / folder / file_name
    # 名字不能以数字开头。先放进 sys.modules，dataclass 才能在加载中途查到自己的模块。
    module_name = "lesson_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_chunks = _load("32_切块.py", "32-文档切块")
_vectors = _load("33_向量.py", "33-向量与相似度")
Chunk = _chunks.Chunk
chunk_markdown = _chunks.chunk_markdown
cosine = _vectors.cosine
embed = _vectors.embed


@dataclass
class Hit:
    """一次命中：哪一块、向量分、关键词分。"""

    chunk: Chunk
    vector_score: float
    keyword_score: float


def build_index(chunks: list[Chunk]) -> list[tuple[Chunk, list[float]]]:
    """每块算一次向量。对照：入库时算，不是用户每问一次都把全文重算。"""
    return [(chunk, embed(chunk.text)) for chunk in chunks]


def keyword_score(question: str, text: str) -> float:
    """问题里的连续数字/字母（如 SKU-8891、400）是否原样出现。没有就 0。"""
    token = _long_token(question)
    if token and token in text:
        return 1.0
    return 0.0


def search(question: str, index: list[tuple[Chunk, list[float]]], k: int = 2) -> list[Hit]:
    """向量分和关键词分都算，按「向量为主、关键词兜底」排序，取前 k 个。"""
    qv = embed(question)
    hits: list[Hit] = []
    for chunk, vec in index:
        hits.append(
            Hit(
                chunk=chunk,
                vector_score=cosine(qv, vec),
                keyword_score=keyword_score(question, chunk.text),
            )
        )
    # 订单号这种要精确匹配：关键词命中时把它顶上去。普通问句主要看向量。
    hits.sort(key=lambda h: (h.keyword_score, h.vector_score), reverse=True)
    return hits[:k]


def _long_token(question: str) -> str:
    """抽出问题里最长的一段「像编号」的字符。没有长度>=4 的就返回空串。"""
    buf = ""
    best = ""
    for ch in question:
        if ch.isalnum() or ch in "-_":
            buf += ch
            if len(buf) > len(best):
                best = buf
        else:
            buf = ""
    return best if len(best) >= 4 else ""


def main() -> None:
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = build_index(chunk_markdown(handbook))
    for question in ("退款几天", "客服电话多少", "SKU-8891 是什么"):
        print("问:", question)
        for hit in search(question, index, k=1):
            print(
                f"  [{hit.chunk.source}] 向量={hit.vector_score:.3f} 关键词={hit.keyword_score:.0f}"
            )
            print(" ", hit.chunk.text)


if __name__ == "__main__":
    main()
