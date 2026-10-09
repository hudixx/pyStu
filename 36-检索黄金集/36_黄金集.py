"""第 36 课示例：固定几道题，看检索到的是不是期望的那一节。

对照 JUnit：改了切块或门槛就重跑，不靠聊天记录里「感觉更好」。
这里评的是检索（出处对不对），不是让另一个模型给回答打分。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# (问题, 期望出处)。None 表示应该拒答。
GOLD: list[tuple[str, str | None]] = [
    ("退款几天", "退款"),
    ("客服电话多少", "客服"),
    ("年度会员多少钱", "价格"),
    ("SKU-8891 是什么", "订单号"),
    ("公司地址在哪", None),
]


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def evaluate(answer_fn, index: list) -> tuple[int, int]:
    """返回 (对的题数, 总题数)。出处列表的第一个要等于期望；拒答时期望是 None。"""
    ok = 0
    for question, expected in GOLD:
        _text, sources = answer_fn(question, index)
        got = sources[0] if sources else None
        mark = "对" if got == expected else "错"
        if got == expected:
            ok += 1
        print(f"{mark}  问={question}  期望={expected}  实际={got}")
    return ok, len(GOLD)


def main() -> None:
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = search.build_index(chunks.chunk_markdown(handbook))
    ok, total = evaluate(cite.answer, index)
    print(f"命中 {ok}/{total}")


if __name__ == "__main__":
    main()
