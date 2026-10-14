"""
设定好黄金集，
用黄金集里面的问题去和向量化后的知识库对比，
得到的答案中，在判定是否必须包含判定的值

"""

from __future__ import annotations

import sys
import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

GOLD: list[tuple[str, str | None, bool]] = [
    ("退款几天", "7", False),  # 正文里要出现「7」。不要求整句一模一样。
    ("客服电话多少", "400-100-1000", False),  # 电话要原样出现。只说「请拨打客服」不算过。
    ("公司地址在哪", None, True),  # 手册里没有地址。必须拒答，要点栏空着。
]

def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "gold44_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def passes(text: str, must: str | None, abstain: bool) -> bool:
    if abstain:
        return "不知道" in text and "北京" not in text
    assert must is not None
    return must in text


def evaluate(answer_fn, index: list) -> tuple[int, int]:
    ok = 0
    for question, must, abstain in GOLD:
        text, _sources = answer_fn(question, index)
        good = passes(text, must, abstain)
        if good:
            ok += 1
        mark = "对" if good else "错"
        print(f"  {mark}  问={question}  答={text}")
    return ok, len(GOLD)

def brief(question: str, index: list) -> tuple[str, list]:
    del index
    if "地址" in question:
        return "不知道，也许我们在北京市，欢迎来访。", ["编造"]
    if "电话" in question:
        return "请拨打客服电话，我们会尽快回复。", ["客服"]
    if "退" in question:
        return  "支持退款，请尽快联系客服办理。", ["退款"]
    return "不知道", []

def main() -> None:
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    # 手册不在本目录。read_text 读成 str。encoding 写明 utf-8，避免 Windows 用 GBK 读坏中文。
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = search.build_index(chunks.chunk_markdown(handbook))

    print("引用版")
    ok , total = evaluate(cite.answer, index)
    print(f"  通过 {ok}/{total}")
    print("简短版")
    ok , total = evaluate(brief, index)
    print(f"  通过 {ok}/{total}")

if __name__ == "__main__":
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""