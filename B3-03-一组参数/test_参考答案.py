"""选修 B3 第 3 课参考答案。题 1 过了。题 2 写在下面。

只跑练习文件是 3 passed。和示例一起跑是 6 passed，多出来的 3 个是示例 test_天数.py。
只跑本文件也是 3 passed。

days(7) 返回「7 天」，7 和天之间有一个空格。0 和 8 都返回「不知道」。
parametrize 只有一个测试函数，三行数据。参数名 n 和 text 对得上。

测试函数的参数没写类型。pytest 不看这个，本课 ruff 也没报。演示里写成了 n: int, expected: str。
你用的名字是 text，不是 expected。名字和上面那一行一致就行。

题 2：
- 三个函数断言是同一句，只是输入不同。断言要改，就得改三处，三份还会慢慢写得不一样。
  参数化是一份断言、三行数据。每一行仍是一次独立的测试，一行失败，另外两行照样跑。
- 失败时测试名里带着这一组的参数。你的三组名字是
  test_days[7-7 天]、test_days[0-不知道]、test_days[8-不知道]。
  看到 8 就知道是第三组，不用猜是 0 还是 8。
"""

from __future__ import annotations

import pytest


def days(n: int) -> str:
    """7 返回「7 天」。别的返回「不知道」。7 和天之间有一个空格。"""

    if n == 7:
        return "7 天"
    return "不知道"


@pytest.mark.parametrize(
    ("n", "text"),
    [
        (7, "7 天"),
        (0, "不知道"),
        (8, "不知道"),
    ],
)
def test_days(n: int, text: str) -> None:
    # 这个函数会跑三次。每一次的 n 和 text 来自上面的一行。
    assert days(n) == text
