"""第 32 课参考答案。题 1 过：四节都在，电话和订单号没有被拆开。

importlib 先放进 sys.modules 再 exec，写法对。文件名以数字开头，不能 import。

题 2：
- 整篇当成一块：输入 token 又贵又慢；出处只能写「全文」；
  向量被各节稀释，问退款也可能检索不到（第 36 课会看见命中下降）。
- overlap 是滑窗时相邻两块重叠的字数。一句话正好切在边界上时，
  两块各自都能看到这句的一部分。本节都很短，这次没有用到滑窗。
- 切得太碎会把 400-100-1000、SKU-8891 拆进不同块，关键词对不上完整编号。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

path = Path(__file__).with_name("32_切块.py")
spec = importlib.util.spec_from_file_location("lesson_chunk32", path)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules["lesson_chunk32"] = mod
spec.loader.exec_module(mod)


def main() -> None:
    handbook = Path(__file__).with_name("手册.md").read_text(encoding="utf-8")
    for i, chunk in enumerate(mod.chunk_markdown(handbook), start=1):
        print(f"{i}. [{chunk.source}] {chunk.text}")


if __name__ == "__main__":
    main()
