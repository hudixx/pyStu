"""第 14 课参考答案：命令行待办。

你已经把「读 JSON → 改数据 → 写回 → 打印」这条链跑通了。
主要差距：题目要的是位置参数 add 买牛奶 / done 1，不是 --title / --todo_id。
done 找不到 id 时不能假装成功。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def data_path() -> Path:
    return Path(__file__).with_name("todos.json")


def load_todos() -> list[dict]:
    path = data_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_todos(items: list[dict]) -> None:
    data_path().write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def next_id(items: list[dict]) -> int:
    """取当前最大 id + 1，空列表从 1 开始。不要用 len+1（以后若删除会撞号）。"""
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def cmd_add(title: str) -> None:
    items = load_todos()
    todo_id = next_id(items)
    items.append({"id": todo_id, "title": title, "done": False})
    save_todos(items)
    print(f"已添加 #{todo_id} {title}")


def cmd_list() -> None:
    items = load_todos()
    if not items:
        print("(空)")
        return
    for item in items:
        mark = "x" if item["done"] else " "
        print(f"[{mark}] #{item['id']} {item['title']}")


def cmd_done(todo_id: int) -> None:
    items = load_todos()
    for item in items:
        if item["id"] == todo_id:
            item["done"] = True
            save_todos(items)
            print(f"已完成 #{todo_id}")
            return
    print(f"找不到 #{todo_id}", file=sys.stderr)
    sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="命令行待办")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="新增")
    p_add.add_argument("title", help="待办内容")  # 位置参数：add 买牛奶

    sub.add_parser("list", help="列出全部")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int)  # 位置参数：done 1
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "add":
        cmd_add(args.title)
    elif args.command == "list":
        cmd_list()
    elif args.command == "done":
        cmd_done(args.id)


if __name__ == "__main__":
    main()
