"""第 25 课示例：一份故意写干净的模块，给 ruff / mypy 当靶子。

对照 Java：
- ruff ≈ Checkstyle（风格和低级错误）
- mypy ≈ javac 的类型检查（可选，默认运行时不会做）

装完 .[lint] 之后：

    python -m ruff check 25-打包与检查/25_检查.py
    python -m mypy 25-打包与检查/25_检查.py

两行都应该没有任何报错。
"""

from __future__ import annotations

from typing import Literal, TypedDict

type Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    """和 21 课同一个形状，给 mypy 一个能分析的函数。"""

    role: Role
    content: str


def only_user(messages: list[ChatMessage]) -> list[ChatMessage]:
    """留下 role 为 user 的消息。纯过滤，没有 IO，所以是普通 def。"""
    return [m for m in messages if m["role"] == "user"]


def main() -> None:
    rows: list[ChatMessage] = [
        {"role": "system", "content": "规则"},
        {"role": "user", "content": "hudi"},
    ]
    kept = only_user(rows)
    print("user 条数 =", len(kept))
    print("内容 =", kept[0]["content"] if kept else "")


if __name__ == "__main__":
    main()
