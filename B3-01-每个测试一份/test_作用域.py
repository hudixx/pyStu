"""选修 B3 第 1 课：fixture 的作用域。每个测试一份，还是整个模块共用一份。

对照 JUnit：scope="function" 像 @BeforeEach，每个测试拿到新的对象。
scope="module" 像 @BeforeAll，这个文件里的测试共用同一份。
yield 之前是准备，yield 之后是清理。对照 @BeforeEach 和 @AfterEach 写在同一个方法里。
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture
def box() -> Iterator[list[str]]:
    """每个测试一个新列表。默认 scope 就是 function。"""

    data: list[str] = []
    yield data  # 测试函数拿到 data。测试结束回到这里。
    data.clear()  # 清理这一份。下一份测试不会看见它，因为下一份是新列表。


@pytest.fixture(scope="module")
def shared() -> list[str]:
    """整个文件只造一次。后面的测试能看见前面测试放进去的东西。"""

    return []


def test_box_first(box: list[str]) -> None:
    box.append("a")
    assert box == ["a"]


def test_box_second(box: list[str]) -> None:
    # 如果这是 module 作用域，这里会看见 ["a"]，断言失败。
    assert box == []


def test_shared_first(shared: list[str]) -> None:
    shared.append("a")
    assert shared == ["a"]


def test_shared_second(shared: list[str]) -> None:
    # 同一个列表。上一个测试放进去的 "a" 还在。
    assert shared == ["a"]
