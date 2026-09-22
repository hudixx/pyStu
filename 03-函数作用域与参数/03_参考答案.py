"""第 03 课参考答案。

题 2 / 3 / 4 以及你额外写的 collect_new，都对。
题 1 的循环是「每次把当前字符串翻倍」，不是「重复 times 次」。
"""


def repeat(text: str, times: int = 2) -> str:
    """字符串 / 列表乘以整数，表示重复，不是数值乘法。"""
    return text * times
    # 你写的：
    #   for i in range(times - 1):
    #       text = text + text
    # times=2 时碰巧对（翻 1 次 → gogo）
    # times=3 时翻 2 次 → go → gogo → gogogogo，得到 4 份，不是 3 份


def collect(item, box=[]):
    """反例：默认 list 在 def 时创建一次，之后每次调用共用。"""
    box.append(item)
    return box


def collect_new(item, box: list[str] | None = None) -> list[str]:
    """正例：默认 None，需要时再新建。你这份已经写对了。"""
    if box is None:
        box = []
    box.append(item)
    return box


def join_names(*names: str, sep: str = ",") -> str:
    """*names 是 tuple；sep 放在 * 后面，只能用关键字传。"""
    return sep.join(names)


def main() -> None:
    print(repeat("go"))     # gogo
    print(repeat("go", 3))  # gogogo

    print(collect("a"))  # ['a']
    print(collect("b"))  # ['a', 'b']  默认 box 是同一张表

    print(collect_new("a"))  # ['a']
    print(collect_new("b"))  # ['b']

    print(join_names("hudi", "ada"))
    print(join_names("hudi", "ada", sep=" | "))


if __name__ == "__main__":
    main()
