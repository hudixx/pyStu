"""第 36 课参考答案。按标题切是 5/5。整篇一块是 1/5。

整篇一块时：
- 退款、客服、价格变成拒答（实际 None）。向量被各节稀释，低于 0.45。
- SKU-8891 关键词仍命中，但出处变成「全文」，不是「订单号」。
- 公司地址本来就该拒答，所以这一题还是对的。

变量名 glod、title 不影响结果。title 其实是题数，不是标题。

题 3：
- 黄金集是固定输入和固定期望，改切块或门槛就重跑。对照 JUnit。
  「又问了一次感觉更好」换了问法、也没有对错标准，改坏了看不出来。
- 它评的是检索出处对不对，不是回答的文采。文采交给阶段九，而且裁判模型也会错。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _load(folder: str, file_name: str):
    path = _ROOT / folder / file_name
    module_name = "ans_" + file_name.replace(".", "_")
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
    gold = _load("36-检索黄金集", "36_黄金集.py")
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")

    index = search.build_index(chunks.chunk_markdown(handbook))
    ok, total = gold.evaluate(cite.answer, index)
    print(f"按标题切 命中 {ok}/{total}")

    bad = search.build_index([chunks.Chunk("全文", handbook)])
    ok_bad, total_bad = gold.evaluate(cite.answer, bad)
    print(f"整篇一块 命中 {ok_bad}/{total_bad}")


if __name__ == "__main__":
    main()
