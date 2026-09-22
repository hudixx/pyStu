"""第 11 课参考答案。

题 1、题 3 对。题 2 输出碰巧两行 pong，但 twice 只调用了一次 ping：
多出来的那行是装饰器自己 print 的，不是第二次调用 func。
"""

from collections.abc import Iterator
from functools import wraps


def evens(limit: int) -> Iterator[int]:
    n = 0
    while n < limit:
        yield n
        n += 2


def twice(func):
    """调用原函数两次，返回第二次的结果。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)            # 第一次，返回值丢掉
        return func(*args, **kwargs)     # 第二次，这个才交出去

    return wrapper


@twice
def ping() -> str:
    print("pong")
    return "ok"


def main() -> None:
    print(list(evens(7)))  # [0, 2, 4, 6]
    print(ping())          # 两行 pong，然后 ok
    print(sum(x for x in range(1, 11) if x % 2 == 1))  # 25


if __name__ == "__main__":
    main()
