"""第 34 课参考答案。三问出处分别是退款、客服、订单号。SKU 的关键词分是 1。

「几天可以退」关键词分是 0，靠向量命中，这正是余弦的用处。
「400-100-1000」关键词分也是 1：编号原样出现在客服那一块里。

importlib 先放进 sys.modules，加载 32 和 34 都对。

题 2：
- 向量库存的是「这段文字的坐标」，用来找最像的几块。
  会员、订单、余额要事务、约束、精确按 id 改，那是普通 SQL。
  对照：搜索索引不是用户表。待办不要写进向量库。
- 完整订单号、完整电话更适合关键词。必须原样出现，差一个字符就不该算命中。
  「几天可以退」这种换说法，关键词经常是 0，要靠余弦。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_chunks = _load(_ROOT / "32-文档切块" / "32_切块.py", "lesson_32")
_search = _load(Path(__file__).with_name("34_检索.py"), "lesson_34_answer")


def main() -> None:
    text = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = _search.build_index(_chunks.chunk_markdown(text))
    for question in ("几天可以退", "400-100-1000", "SKU-8891"):
        hit = _search.search(question, index, k=1)[0]
        print(hit.chunk.source, f"{hit.vector_score:.3f}", hit.keyword_score, hit.chunk.text)


if __name__ == "__main__":
    main()
