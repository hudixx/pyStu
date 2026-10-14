"""第 44 课示例：固定问题和期望要点，给回答打分。不评文采。

对照 JUnit。第 36 课评的是检索出处。这一课评的是回答正文里有没有要点。
「简短礼貌」的版本会掉分。掉分是表格上的数字，不是聊天里的感觉。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# (问题, 要点, 是否必须拒答)。
# 要点是 None 且必须拒答：正文里要有「不知道」，不能编出一个城市。
# 全大写是约定，不是语言强制的常量。
GOLD: list[tuple[str, str | None, bool]] = [
    ("退款几天", "7", False),
    ("客服电话多少", "400-100-1000", False),
    ("公司地址在哪", None, True),
]


def _load(folder: str, file_name: str):
    """文件名以数字开头，import 语句写不出来。"""
    path = _ROOT / folder / file_name
    module_name = "gold44_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # 先登记，dataclass 执行时才找得到自己。
    spec.loader.exec_module(module)
    return module


def passes(text: str, must: str | None, abstain: bool) -> bool:
    """一条规则。拒答看有没有「不知道」，以及有没有编城市。其余看要点是不是子串。"""
    if abstain:
        # 编了北京仍含「不知道」也不算过。两个条件都要。
        return "不知道" in text and "北京" not in text
    # must 在非拒答的题里不会是 None。这里收窄，是给类型检查看的。
    assert must is not None
    return must in text


def evaluate(answer_fn, index: list) -> tuple[int, int]:
    """返回 (对的题数, 总题数)。answer_fn 是函数本身，调用时传进去，不要先加括号。"""
    ok = 0
    for question, must, abstain in GOLD:
        text, _sources = answer_fn(question, index)
        good = passes(text, must, abstain)
        if good:
            ok += 1
        mark = "对" if good else "错"
        print(f"  {mark}  问={question}  答={text}")
    return ok, len(GOLD)


def brief(question: str, index: list) -> tuple[str, list[str]]:
    """「感觉更礼貌」的一版。不写数字，地址题还编了一个城市。index 不用，签名要和第 35 课对齐。"""
    del index  # 明确丢掉。不写这行也会跑，但读代码的人会以为漏了。
    if "地址" in question:
        return "我们在北京市海淀区，欢迎来访。", ["编造"]
    if "电话" in question:
        return "请拨打客服电话，我们会尽快回复。", ["客服"]
    if "退" in question:
        return "支持退款，请尽快联系客服办理。", ["退款"]
    return "不知道", []


def main() -> None:
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = search.build_index(chunks.chunk_markdown(handbook))

    print("引用版")
    ok, total = evaluate(cite.answer, index)
    print(f"  通过 {ok}/{total}")

    print("简短版")
    ok_brief, total_brief = evaluate(brief, index)
    print(f"  通过 {ok_brief}/{total_brief}")


if __name__ == "__main__":
    main()
