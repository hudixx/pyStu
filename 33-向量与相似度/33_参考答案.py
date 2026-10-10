"""第 33 课参考答案。三个数大约是 0.654、0.036、0.595。

第一个大于第二个，第三个明显高于 0。方向对。
加载时模块名写成了 chunk_markdown，那是第 32 课的名字。能跑，但以后查 sys.modules 会对不上。
33_向量.py 没有 dataclass，所以这次没炸。名字写成 lesson_vec33 更清楚。

题 2：
- LIKE 回答「这段字符在不在」，结果是真或假。「退款几天」里没有完整的
  「购买后 7 天内可以退款」，LIKE 对不上。
  余弦回答「两个向量方向像不像」，是一个小数。共享「退款」相关的维时会接近。
- 内置 hash() 每次启动进程会变（PYTHONHASHSEED）。同一句话两次向量不同，
  入库时的向量和查询时的向量对不上。要用 md5 这种稳定算法。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

path = Path(__file__).with_name("33_向量.py")
spec = importlib.util.spec_from_file_location("lesson_vec33", path)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules["lesson_vec33"] = mod
spec.loader.exec_module(mod)


def main() -> None:
    embed = mod.embed
    cosine = mod.cosine
    print(round(cosine(embed("退款几天"), embed("购买后 7 天内可以退款")), 3))
    print(round(cosine(embed("退款几天"), embed("月度会员 99 元")), 3))
    print(round(cosine(embed("客服电话"), embed("客服电话是 400-100-1000")), 3))


if __name__ == "__main__":
    main()
