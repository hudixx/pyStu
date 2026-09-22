"""第 08 课参考答案。

题 1 结构对，差在没把 int(raw) 的结果存下来，else 里应打印数字不是原始字符串。
题 2 / 3 已做对。空类体不能什么都不写，docstring 或 pass 二选一即可。
"""

from pathlib import Path


class AgeError(Exception):
    """年龄不合法。类体不能完全空着，写 docstring 或 pass 都行。"""


def parse_int(raw: str) -> None:
    try:
        n = int(raw)  # 存下来，else 才能打印「数字」
    except ValueError:
        print(f"失败: {raw}")
    else:
        print(f"成功: {n}")


def set_age(age: int) -> int:
    if age < 0:
        raise AgeError("年龄不能为负")
    return age  # 不必再写 else，raise 已经结束函数


def main() -> None:
    parse_int("42")
    parse_int("x")

    try:
        set_age(-1)
    except AgeError as e:
        print(e)

    path = Path(__file__).with_name("note.txt")
    with path.open("w", encoding="utf-8") as f:
        f.write("hudi 学 Python")
    with path.open("r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()
