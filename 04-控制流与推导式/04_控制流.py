"""第 04 课示例：if/elif、三元、enumerate、for/else、推导式。

对照 Java：
- else if → elif
- cond ? a : b → a if cond else b（顺序相反）
- 增强 for → for x in xs
- Stream map/filter → 推导式
"""


def demo_if_and_ternary() -> None:
    """elif 是一个词；三元表达式先写结果再写条件。"""
    print("=== if / 三元 ===")
    score = 75
    if score >= 90:
        grade = "A"
    elif score >= 60:
        grade = "B"
    else:
        grade = "C"
    print("grade =", grade)

    n = -3
    # Java: n > 0 ? "正" : "非正"
    label = "正" if n > 0 else "非正"
    print("label =", label)


def demo_for() -> None:
    """优先按元素遍历；需要下标时用 enumerate。"""
    print("=== for / enumerate / zip ===")
    langs = ["java", "python", "go"]

    for lang in langs:
        print("元素:", lang)

    for index, lang in enumerate(langs, start=1):
        print(f"{index}. {lang}")

    years = [30, 1, 2]
    for lang, year in zip(langs, years):
        print(f"{lang} 学了 {year} 年")


def demo_for_else() -> None:
    """else 紧跟 for：只有循环没被 break，才会走进 else。"""
    print("=== for/else ===")
    langs = ["java", "python"]
    needle = "go"
    for lang in langs:
        if lang == needle:
            print("找到了")
            break
    else:
        print("没找到")  # 全程没有 break，所以会打印这句


def demo_comprehension() -> None:
    """推导式对照 Stream：要什么 for 从哪来 if 过滤。"""
    print("=== 推导式 ===")
    nums = [0, 1, 2, 3, 4, 5]
    even_squares = [n * n for n in nums if n % 2 == 0]
    print("偶数的平方:", even_squares)  # [0, 4, 16]

    unique_len = {len(s) for s in ["java", "go", "rust", "python"]}
    print("长度集合:", unique_len)

    user = {"name": "hudi", "city": "上海"}
    echoed = {key: value for key, value in user.items()}
    print("dict 推导:", echoed)


def main() -> None:
    demo_if_and_ternary()
    demo_for()
    demo_for_else()
    demo_comprehension()


if __name__ == "__main__":
    main()
