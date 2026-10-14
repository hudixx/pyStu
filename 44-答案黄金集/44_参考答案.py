"""第 44 课参考答案。引用版 3/3，简短版 0/3。

你的两版分数是对的。两处和结果有关的写法：

- print("简短版") 写在第二次 evaluate 之后。分数先打出来，标题后出现。
  看输出时，第二段 0/3 才是简短版。
- 简短版的地址题写成「不知道，也许我们在北京市」。
  你的 passes 里还有「北京」 not in text，所以这题不及格。
  如果只查「不知道」，这句会算过，简短版就变成 1/3，不是 0/3。
  示例里的简短版根本不说「不知道」，单靠这一处就会不及格，所以示例把「北京」删了。
  你这句同时拒答又编城市，「北京」那半句才真的在起作用。

文件开头那段话把步骤说拧了。黄金集不是拿问题去和向量比。
cite.answer 先检索再给出正文；passes 只看正文里有没有要点。
brief 把 index 丢掉了，根本没查知识库。

题 3：
- 简短版读起来更客气，比如「支持退款，请尽快联系客服」，但没有「7」。
  只凭客气就当成更好，天数丢了也看不出来。同一批题重跑，分数是 0/3。
- 这一课评回答正文里的要点：有没有「7」、有没有电话、拒答题有没有「不知道」。
  第 36 课评检索出处，比如是不是「退款」那一节。
  出处对了、正文把天数说丢：第 36 课仍算过，这一课算不过。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

GOLD: list[tuple[str, str | None, bool]] = [
    ("退款几天", "7", False),
    ("客服电话多少", "400-100-1000", False),
    ("公司地址在哪", None, True),
]


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "ans44_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def passes(text: str, must: str | None, abstain: bool) -> bool:
    """拒答题只看有没有「不知道」。这版简短回答本身就不含这四个字。"""
    if abstain:
        return "不知道" in text
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


def brief(question: str, index: list) -> tuple[str, list[str]]:
    """地址题不写「不知道」，直接编一个地址。这样只查「不知道」也会不及格。"""
    del index
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
