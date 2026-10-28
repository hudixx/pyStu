"""选修 B3 第 3 课：同一条断言，换几组参数。

对照 @ParameterizedTest 配 @CsvSource。失败时报告里能看见是哪一组。
不要复制三份几乎一样的测试函数。
"""

from __future__ import annotations

import pytest


def days(n: int) -> str:
    """7 返回「7 天」。别的返回「不知道」。7 和天之间有一个空格。

    这是被测的普通函数，不是测试。pytest 不会因为它不以 test_ 开头就去跑它。
    n: int 只是标注。真传入 7.0 这种浮点，解释器也不会在这里拦，除非另外跑 mypy。
    """

    if n == 7:
        # == 对整数比的是数值。对照 ==。这里没有对象身份的问题。
        return "7 天"  # 引号里 7 和天之间有一个空格。断言时期望字符串必须一模一样，多一个空格就不等于。
    return "不知道"  # 上面的 if 没进去才走到这里。对照 else，但 if 里已经 return，后面不用再写 else。


@pytest.mark.parametrize(
    # 第一段是参数名，写成元组。圆括号加逗号就是元组，对照一对不能改的值。
    # 字符串 "n" 和 "expected" 必须和下面测试函数的参数名一致。pytest 靠名字填，不靠顺序猜类型。
    ("n", "expected"),
    # 第二段是各组参数，一个列表。列表里每个小元组是一组。对照三行 CSV，每行两个字段。
    [
        (7, "7 天"),  # 这一组：n=7，expected="7 天"。days(7) 对得上。
        (0, "不知道"),  # n=0，不是 7，函数走下面的 return。
        (8, "不知道"),  # n=8，同样不是 7。
    ],
)
def test_days(n: int, expected: str) -> None:
    # 装饰器让 pytest 把这个函数跑三次，每次代入一组。失败的报告里会标出是哪一组。
    # 这一行会跑三次。每一次的 n 和 expected 来自上面的一行。
    # days(n) 才是调用。assert 比较返回值和这一组的期望。对照 assertEquals(expected, days(n))。
    assert days(n) == expected
