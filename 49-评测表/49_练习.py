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

"""
 题3不知道，请在参考答案的注释中个给出
"""