"""第 13 课参考答案。

题 1 / 2 对。题 3 打出了带时区的 datetime，但格式不是题目要的 YYYY-MM-DD HH:MM。
strftime 是 datetime 的方法，不要 from time import strftime。
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="第 13 课练习")
    parser.add_argument("--text", required=True)
    parser.add_argument("--times", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(args.text * args.times)

    counts = Counter(["java", "python", "java", "go", "python", "java"])
    print(counts["java"])  # 3；Counter 是 dict 子类，直接 counts["java"] 即可
    print(counts.most_common(2))

    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    print(now.strftime("%Y-%m-%d %H:%M"))


if __name__ == "__main__":
    main()
