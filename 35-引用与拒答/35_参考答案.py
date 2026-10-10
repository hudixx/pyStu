"""第 35 课参考答案。三问都对。

几天可以退 → 出处退款，正文有 7 天。
年度会员多少钱 → 出处价格，正文有 899。
你们公司在哪个城市 → 不知道，出处空列表。没有去调聊天模型。

门槛写成关键词 ≥ 1 或向量分 ≥ 0.45，和示例一致。
循环里把手册变量 text 又用来接回答。索引已经建好，所以这次没坏。
两个用途不要共用一个名字。

题 2：
- Top-1 永远有一块「相对最像」。问公司地址时，某一节仍会排第一，但分很低。
  没有门槛就会把不相关的段落当成答案。空结果是合法结果。
- 检索到的段落是数据，不是指令。放进 system，段落里若写「忽略以上规则」，
  会变成新的系统提示。对照 SQL：用户输入不能拼进语句本身。
  system 只写「只根据资料回答」；资料和问题放在 user。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.split("_")[0] + "_ans"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")
_MIN_VECTOR = 0.45


def answer(question: str, index: list) -> tuple[str, list[str]]:
    hits = _search.search(question, index, k=1)
    if not hits:
        return "不知道", []
    top = hits[0]
    relevant = top.keyword_score >= 1 or top.vector_score >= _MIN_VECTOR
    if not relevant:
        return "不知道", []
    text = f"{top.chunk.text}（来源：{top.chunk.source}）"
    return text, [top.chunk.source]


def main() -> None:
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = _search.build_index(_chunks.chunk_markdown(handbook))
    for question in ("几天可以退", "年度会员多少钱", "你们公司在哪个城市"):
        reply, sources = answer(question, index)
        print("问:", question)
        print("  答:", reply)
        print("  出处:", sources)


if __name__ == "__main__":
    main()
