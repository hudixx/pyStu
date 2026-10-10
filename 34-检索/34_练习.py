import sys
from pathlib import Path
import importlib.util

parent_path = Path(__file__).resolve().parent.parent

path_32 = parent_path / "32-文档切块" / "32_切块.py"
path_34 = Path(__file__).with_name("34_检索.py")

def _load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

mod_32 =  _load_module(path_32, "lesson_32")
mod_34 = _load_module(path_34, "lesson_34")

chunk_markdown = mod_32.chunk_markdown
build_index  = mod_34.build_index
search = mod_34.search

def main() -> None:
    text = (parent_path / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = build_index(chunk_markdown(text))

    for hit in search("几天可以退", index , 1):
        print(hit.chunk.source, hit.vector_score, hit.keyword_score,  hit.chunk.text)

    for hit in search("400-100-1000", index , 1):
        print(hit.chunk.source, hit.vector_score, hit.keyword_score,  hit.chunk.text)

    for hit in search("SKU-8891", index , 1):
        print(hit.chunk.source, hit.vector_score, hit.keyword_score,  hit.chunk.text)


if __name__ == "__main__":
    main()

""" 
题2不知道，请在参考答案的注释中个给出
"""



