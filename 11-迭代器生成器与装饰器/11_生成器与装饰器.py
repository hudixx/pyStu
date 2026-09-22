"""第 11 课示例：yield 生成器、装饰器。

对照 Java：
- yield ≈ 惰性 Iterator / Stream
- @decorator ≈ 轻量 AOP
"""

from functools import wraps
from collections.abc import Iterator


def countdown(n: int) -> Iterator[int]:
    """每次 yield 一个数，不会一次性造出完整列表。"""
    while n > 0:
        yield n
        n -= 1


def logged(func):
    """无参装饰器：调用前后打日志。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"→ 进入 {func.__name__} args={args}")
        result = func(*args, **kwargs)
        print(f"← 离开 {func.__name__} 返回 {result}")
        return result

    return wrapper


@logged
def add(a: int, b: int) -> int:
    return a + b


def main() -> None:
    print("=== 生成器 ===")
    for x in countdown(3):
        print("yield 出", x)

    gen = countdown(2)
    print("next 第一次", next(gen))
    print("next 第二次", next(gen))
    try:
        next(gen)
    except StopIteration:
        print("生成器耗尽，再 next 会 StopIteration")

    print("=== 生成器表达式 ===")
    print(sum(x * x for x in range(5)))  # 0+1+4+9+16=30
    print("=== 装饰器 ===")
    print("最终结果", add(1, 2))
    print("函数名仍是", add.__name__)  # 因为用了 wraps


if __name__ == "__main__":
    main()
