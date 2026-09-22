"""第 04 课参考答案。

四道题你都做对了。下面按题目原样写一份更直白的版本，
方便对照：不一定要包成 *args，对列表直接 for / 推导即可。
"""


def sign_of(n: int) -> str:
    """三元顺序：真值 if 条件 else 假值。你这份已经写对。"""
    return "正" if n > 0 else "非正"


def main() -> None:
    print(sign_of(3))
    print(sign_of(0))

    langs = ["java", "python", "go"]
    for index, lang in enumerate(langs, start=1):
        print(f"{index}. {lang}")

    nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print([n * n for n in nums if n % 2 == 0])


if __name__ == "__main__":
    main()
