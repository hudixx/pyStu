"""第 01 课参考答案。

对照你的 01_练习.py 看三件事：
1. 声明了 -> str，就要 return，不要在函数里 print
2. if value: 表示「有内容」，假值才是「空」
3. 题 2 要用多组输入把真值表跑一遍
"""


def introduce(name: str, years: int) -> str:
    """按题目要求返回一句话，不负责打印。"""
    # 函数的职责是「算出结果并交出去」；谁调用，谁决定要不要 print
    return f"我是 {name}，学编程 {years} 年。"


def label(value) -> str:
    """假值返回「空」，真值返回「有内容」。"""
    # if value: 会走「真」分支。假值包括 None / 0 / "" / [] / {} / False
    if value:
        return "有内容"
    return "空"


def main() -> None:
    """入口只负责调用和打印，方便一眼看清返回值。"""
    print(introduce("hudi", 30))

    # 题 2 要求分别传入这些值，不要只测 None
    samples = ["", "hello", 0, 1, None, []]
    for item in samples:
        # !r 会带引号打印，空字符串也能看出来
        print(f"label({item!r}) -> {label(item)}")


if __name__ == "__main__":
    main()
