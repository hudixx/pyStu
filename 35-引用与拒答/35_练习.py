import sys
from pathlib import Path
import importlib.util

_ROOT = Path(__file__).resolve().parent.parent

def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.split("_")[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
lesson_32 = _load("32-文档切块", "32_切块.py")
lesson_34 = _load("34-检索", "34_检索.py")
_MIN_VECTOR = 0.45

def answer(question: str, index: list) -> tuple[str, list[str]]:
    hits = lesson_34.search(question, index, 1)
    if not hits:
        return "不知道" , []
    top = hits[0]
    has = top.keyword_score >= 1 or top.vector_score >= _MIN_VECTOR
    if not has:
        return "不知道" , []
    text = f"{top.chunk.text} (来源： {top.chunk.source})"
    return text, [top.chunk.source]

def main() -> None:
    text = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = lesson_34.build_index(lesson_32.chunk_markdown(text))
    for question in ["几天可以退","年度会员多少钱","你们公司在哪个城市"]:
        text, sources = answer(question, index)
        print("问:", question)
        print("  答:", text)
        print("  出处:", sources)


if __name__ == "__main__":
    main()

"""
    题2不知道，请在参考答案的注释中个给出
"""