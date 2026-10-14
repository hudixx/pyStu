"""第 49 课示例：用 pandas 读第 44 课那种评测表，算出两版的通过率。

对照：SELECT 版本, AVG(通过) FROM eval GROUP BY 版本。
不是转数据分析。只会读、过滤、按组取平均。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# 和本文件同目录。不依赖你从哪个目录启动。
_CSV = Path(__file__).resolve().parent / "评测结果.csv"


def main() -> None:
    # read_csv 得到一张表。对照从 CSV 读进一个 List，但带列名，可以按列算。
    frame = pd.read_csv(_CSV)
    print("行数", len(frame))

    # groupby：按「版本」分组。mean 是组里「通过」这一列的平均。1 全过，0 全不过。
    # as_index=False：版本仍是普通列，不要变成索引。打印时更好读。
    rate = frame.groupby("版本", as_index=False)["通过"].mean()
    print(rate.to_string(index=False))

    # 两个条件用 &，每一边要加括号。对照 SQL 的 WHERE 版本 = '简短版' AND 通过 = 0。
    failed = frame[(frame["版本"] == "简短版") & (frame["通过"] == 0)]
    print("简短版失败", len(failed), "条")


if __name__ == "__main__":
    main()
