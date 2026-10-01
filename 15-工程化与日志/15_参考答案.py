"""第 15 课参考答案。

你的 basicConfig、getLogger(__name__)、除零时 raise，方向对。
题 1 差在：成功路径没打 info；try 里写的是 logger.info((1, 0))，并没有调用 divide(1, 0)。
"""

from __future__ import annotations

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def divide(a: int, b: int) -> float:
    """正常记 info；除零先 error 再抛，让调用方决定怎么收。"""
    if b == 0:
        logger.error("除零: a=%s b=%s", a, b)
        raise ZeroDivisionError("除数不能为 0")
    logger.info("计算 %s / %s", a, b)
    return a / b


def main() -> None:
    print(divide(8, 2))
    try:
        print(divide(1, 0))
    except ZeroDivisionError:
        logger.error("已捕获除零，程序继续")


if __name__ == "__main__":
    main()
