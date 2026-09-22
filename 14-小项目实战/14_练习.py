import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class InsertData:
    id: int
    title: str
    done: bool

def data_path() -> Path:
    return Path(__file__).resolve().parent / "todos.json"

def load_todos() -> list[dict]:
    path = data_path()
    if not path.exists():
        return []
    jsons = json.loads(path.read_text(encoding="utf-8"))
    return [] if jsons is None else jsons

def save_todos(items: list[dict]) -> None:
    path = data_path()
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def cmd_add(title: str) -> None:
    items = load_todos()
    id_it = len(items) + 1
    if id_it == 1:
        items.append({ "id": id_it, "title": title, "done": False})
    else:
        items.append({"id": id_it, "title": title, "done": False})

    save_todos(items)
    print(f"已添加 #{id_it} {title}")

def cmd_list(items: list[dict]) -> None:
    for item in items:
        print(f"[{ 'x' if item['done'] else ' ' }] #{item['id']} {item['title']}")

def cmd_done(todo_id) -> None:
    items = load_todos()
    for item in items:
        if todo_id == item['id']:
            item['done'] = True
            save_todos(items)
            print(f"已完成 #{todo_id}")
            return
    print(f"找不到 #{todo_id}", file=sys.stderr)
    sys.exit(1)

def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='演示')
    sub = parser.add_subparsers(dest='command', required=True)
    s_add = sub.add_parser("add", help="添加的文字")
    s_add.add_argument("title", type=str, required=True)
    sub.add_parser("list")
    s_done = sub.add_parser("done")
    s_done.add_argument("todo_id", type=int, required=True)
    return parser

def main() -> None:
    # path_temp = data_path()
    args = parse_args().parse_args()
    if args.command == "add":
        cmd_add(args.title)
    elif args.command == "list":
        cmd_list(load_todos())
    elif args.command == "done":
        cmd_done(args.todo_id)
    #对照题
    """
    不知道,请给我答案,要简洁明要
    
    """

if __name__ == "__main__":
    main()