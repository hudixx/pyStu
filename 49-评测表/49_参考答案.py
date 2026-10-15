"""第 49 课参考答案。题 1、题 2 都过。阶段九结束。

行数 6。引用版通过率 1.0，简短版 0.0。简短版失败 3 条。
数字是从 评测结果.csv 算出来的，不是手写后再打印。
过滤用了 &，并且两边加了括号。这是对的。写成 and 会报错。

题 3：
- groupby("版本")["通过"].mean() 对标
  SELECT 版本, AVG(通过) FROM 评测结果 GROUP BY 版本。
  1 是全过，0 是全不过，平均就是这一版的通过率。
- 「简短版读起来更舒服」没有对错。同一批题落成表之后，简短版是 0.0，引用版是 1.0。
  舒服弥补不了缺掉的「7」、电话和「不知道」。该用哪一版，看这张表，不看读起来的感觉。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_CSV = Path(__file__).resolve().parent / "评测结果.csv"


def main() -> None:
    frame = pd.read_csv(_CSV)
    print("行数", len(frame))
    rate = frame.groupby("版本", as_index=False)["通过"].mean()
    print(rate.to_string(index=False))
    failed = frame[(frame["版本"] == "简短版") & (frame["通过"] == 0)]
    print("简短版失败", len(failed), "条")


if __name__ == "__main__":
    main()
