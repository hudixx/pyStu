"""选修 B3 第 1 课参考答案。题 1 过了。题 2 写在下面。

只跑这个文件是 2 passed。和示例一起跑是 6 passed，多出来的 4 个是示例自己的测试。

fixture 名叫 box，没有写 scope，所以是默认的 function。
两个测试各自 append 之后，长度都是 1。第二个测试没有看见第一个放进去的 "a"。

用 return 交出空列表，这题够用。yield 是测试结束之后还要做清理时才需要。
函数和函数之间少了一行空行。ruff 的 E302 要求顶层函数之间空两行。不影响这次测试。

题 2：
- function 是每个测试造一份，对照 @BeforeEach。这是默认值。
  module 是这个文件只造一份，对照 @BeforeAll。前面的测试改过的内容会留到后面。
- 第二个测试看到长度 2，说明两份测试拿到的是同一个列表。
  第一个测试 append 的东西还在。夹具被共享了，不是每个测试一份新的。
"""

from __future__ import annotations

import pytest


@pytest.fixture
def box() -> list[str]:
    """默认作用域。每个测试拿到一个新的空列表。"""

    return []


def test_box_first(box: list[str]) -> None:
    box.append("a")
    assert len(box) == 1


def test_box_second(box: list[str]) -> None:
    box.append("b")
    # 如果和上一个测试共用同一个列表，这里会是 2。
    assert len(box) == 1
