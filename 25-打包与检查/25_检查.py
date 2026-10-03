"""第 25 课示例：一份故意写干净的模块，给 ruff / mypy 当靶子。

对照 Java：
- ruff ≈ Checkstyle（风格和低级错误，例如未使用变量、未定义名）
- mypy ≈ javac 的类型检查（可选；默认运行时不会做）
- pytest 才是测试；pydantic 才是运行时校验请求体。这两个检查器都不执行业务

装完 .[lint] 之后：

    PYTHONUTF8=1 python 25-打包与检查/25_检查.py
    python -m ruff check 25-打包与检查/25_检查.py
    python -m mypy 25-打包与检查/25_检查.py

后两行都应该没有任何报错（exit code 0）。
"""

from __future__ import annotations

# Literal：值只能是列出的那几个字符串。对照枚举或 @StringDef，但运行时默认不拦。
# TypedDict：dict 的键和值类型。对照 Map 太松、又想给检查器看结构时用。
from typing import Literal, TypedDict

# type Role = ...：3.12+ 的类型别名。给 Role 起名，避免到处写一长串 Literal。
# 对照 typedef / type alias。运行时几乎等于注解，mypy 会当真。
type Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    """和 21 课同一个形状，给 mypy 一个能分析的函数。

    TypedDict 不是 pydantic BaseModel：
    - 这是给类型检查看的 dict 形状，构造时不会校验
    - 线上 JSON 仍要用 pydantic（17 课）挡非法数据
    对照：静态的 DTO 形状 vs Bean Validation。
    """

    role: Role      # 只能是 system / user / assistant，写成 "admin" mypy 会报
    content: str    # 必须是字符串键 content


def only_user(messages: list[ChatMessage]) -> list[ChatMessage]:
    """留下 role 为 user 的消息。纯过滤，没有 IO，所以是普通 def。

    没有 await 就不要写成 async def（24 课那条规则）。
    列表推导对照 stream().filter(...).toList()。
    """
    return [m for m in messages if m["role"] == "user"]


def main() -> None:
    """构造两条消息，过滤后应只剩 user 那条。注解写清楚，ruff/mypy 才有东西可查。"""
    # rows: list[ChatMessage]：告诉 mypy 这是消息列表，不是随意的 list[dict]。
    # 缺键、role 写成别的字符串，mypy 会在这一行附近报错。
    rows: list[ChatMessage] = [
        {"role": "system", "content": "规则"},
        {"role": "user", "content": "hudi"},
    ]
    kept = only_user(rows)
    print("user 条数 =", len(kept))  # 应为 1
    # kept 可能为空时不要硬取 [0]。本例一定有 user，右边的 if 是防御写法。
    print("内容 =", kept[0]["content"] if kept else "")


if __name__ == "__main__":
    main()
