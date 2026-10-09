"""第 35 课示例：有命中才回答，并带上出处；没有就说不知道。

本课不打聊天模型。答案先用命中的原文，避免假模型把资料回声一遍。
真环境把「原文」换成一次 chat：system 写「只根据资料回答」，资料放进 user。
没命中时仍然不要调用模型。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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

# 向量分低于这个值，且关键词也没命中，就当没检索到。
# 假向量上「退款几天」大约 0.7，「公司地址」接近 0。换真 embedding 要重调这个数。
_MIN_VECTOR = 0.45


def answer(question: str, index: list) -> tuple[str, list[str]]:
    """返回 (回答, 出处列表)。出处为空表示拒答。"""
    hits = _search.search(question, index, k=1)
    if not hits:
        return "不知道", []
    top = hits[0]
    relevant = top.keyword_score >= 1 or top.vector_score >= _MIN_VECTOR
    if not relevant:
        return "不知道", []
    # 先把资料原句交出去，并写明来自哪一节。模型改写时也必须保留这个来源。
    text = f"{top.chunk.text}（来源：{top.chunk.source}）"
    return text, [top.chunk.source]


def main() -> None:
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = _search.build_index(_chunks.chunk_markdown(handbook))
    for question in ("退款几天", "SKU-8891 是什么", "公司地址在哪"):
        text, sources = answer(question, index)
        print("问:", question)
        print("  答:", text)
        print("  出处:", sources)


if __name__ == "__main__":
    main()
