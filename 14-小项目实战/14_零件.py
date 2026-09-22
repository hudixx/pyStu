"""第 14 课零件：子命令 + JSON 读写。

这不是完整待办，只演示两块积木。作业请自己写 14_练习.py。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def demo_path() -> Path:
    """数据文件放在脚本旁边，不要写死盘符。"""
    return Path(__file__).with_name("零件演示.json")


def load_items(path: Path) -> list[dict]:
    """文件不存在就当成空列表——第一次运行常见。"""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_items(path: Path, items: list[dict]) -> None:
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="零件演示，不是完整待办")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="往演示文件里塞一条")
    p_add.add_argument("--title", required=True)

    sub.add_parser("list", help="打印演示文件")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    path = demo_path()
    items = load_items(path)

    if args.command == "add":
        items.append({"title": args.title})
        save_items(path, items)
        print("已写入零件演示.json，条数:", len(items))
    elif args.command == "list":
        if not items:
            print("(空)")
        for i, row in enumerate(items, start=1):
            print(f"{i}. {row['title']}")


if __name__ == "__main__":
    main()
