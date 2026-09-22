"""第 13 课示例：argparse、datetime、Counter。

    PYTHONUTF8=1 python 13-标准库与生态/13_标准库.py --name hudi
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="标准库小演示")
    parser.add_argument("--name", default="陌生人", help="你的名字")
    parser.add_argument(
        "--langs",
        nargs="*",
        default=["java", "python", "java", "go", "java"],
        help="语言列表，可重复",
    )
    return parser.parse_args()


def now_shanghai() -> datetime:
    """IANA 时区在 Windows 上经常缺数据，缺则退回本地时区并提示。"""
    try:
        return datetime.now(ZoneInfo("Asia/Shanghai"))
    except Exception:
        print("提示: 本机没有时区数据，可执行 python -m pip install tzdata")
        return datetime.now().astimezone()


def main() -> None:
    args = parse_args()
    now = now_shanghai()
    tomorrow = now + timedelta(days=1)

    print(f"你好, {args.name}")
    print("现在:", now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("明天:", tomorrow.date().isoformat())

    counts = Counter(args.langs)
    print("语言计数:", dict(counts))
    print("最多的:", counts.most_common(1))


if __name__ == "__main__":
    main()
