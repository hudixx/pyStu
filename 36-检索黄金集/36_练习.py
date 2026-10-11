import sys
from pathlib import Path
import importlib.util
_root = Path(__file__).resolve().parent.parent

def _load(folder: str, file_name: str):
    path = _root / folder / file_name
    module_name = "lesson_" + file_name.split("_")[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main() -> None:
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    glod = _load("36-检索黄金集", "36_黄金集.py")

    handbook = (_root / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = search.build_index(chunks.chunk_markdown(handbook))
    ok , title = glod.evaluate(cite.answer, index)
    print(f"命中： {ok}/{title}")

    index_all = search.build_index([chunks.Chunk("全文",handbook)])
    ok_all , title_all = glod.evaluate(cite.answer, index_all)
    print(f"命中： {ok_all}/{title_all}")
if __name__ == "__main__":
    main()

"""
题3不知道，请在参考答案的注释中个给出
"""