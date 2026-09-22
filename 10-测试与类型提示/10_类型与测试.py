"""第 10 课示例：类型注解长什么样（运行时不会因为注解失败）。"""


def greet(name: str | None) -> str:
    """name 可以是 str，也可以是 None。"""
    if name is None:
        return "你好, 陌生人"
    return f"你好, {name}"


def add(a: int, b: int) -> int:
    """注解写 int，但运行时不检查。传两个 str 会拼成一个 str。"""
    return a + b


def main() -> None:
    print(greet("hudi"))
    print(greet(None))
    print("add(1, 2) =", add(1, 2))
    # 注解挡不住错误类型：运行时 str+str 得到 'ab'
    print("add('a', 'b') =", add("a", "b"))  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
