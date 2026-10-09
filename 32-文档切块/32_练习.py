import sys
from pathlib import Path
import importlib.util
path = Path(__file__).with_name("32_切块.py")
spec = importlib.util.spec_from_file_location("lesson_chunk32", path)
mod = importlib.util.module_from_spec(spec)
sys.modules["lesson_chunk32"] = mod
spec.loader.exec_module(mod)
chunk_markdown = mod.chunk_markdown

def main() -> None:
    handbook = Path(__file__).with_name("手册.md").read_text(encoding="utf-8")
    for i , chunk in enumerate(chunk_markdown(handbook), start=1):
        print(f"{i}. [{chunk.source}] {chunk.text}")


if __name__ == "__main__":
    main()

"""
题2不知道，请在参考答案的注释中个给出
"""