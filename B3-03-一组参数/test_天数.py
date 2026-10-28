"""选修 B3 第 3 课：同一条断言，换几组参数。

对照 @ParameterizedTest 配 @CsvSource。失败时报告里能看见是哪一组。
不要复制三份几乎一样的测试函数。
"""

from __future__ import annotations

import pytest


def days(n: int) -> str:
    """7 返回「7 天」。别的返回「不知道」。7 和天之间有一个空格。"""

    if n == 7:
        return "7 天"
    return "不知道"


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (7, "7 天"),
        (0, "不知道"),
        (8, "不知道"),
    ],
)
def test_days(n: int, expected: str) -> None:
    # 这一行会跑三次。每一次的 n 和 expected 来自上面的一行。
    assert days(n) == expected
