"""选修 B3 第 1 课：fixture 的作用域。每个测试一份，还是整个模块共用一份。

对照 JUnit：scope="function" 像 @BeforeEach，每个测试拿到新的对象。
scope="module" 像 @BeforeAll，这个文件里的测试共用同一份。
yield 之前是准备，yield 之后是清理。对照 @BeforeEach 和 @AfterEach 写在同一个方法里。

本文件没有 main。pytest 会自己找出名字以 test_ 开头的函数来跑。这是 pytest 的约定，不是 Python 语法。
直接 python 本文件不会跑这些测试，因为它不调用它们。
"""

# 推迟注解求值。Iterator[list[str]] 这种写法在 import 时不会立刻执行。
from __future__ import annotations

# Iterator 是「这个函数里有 yield」的类型标注。对照一个会先交出值、之后还能继续跑的方法，不是返回 List。
from collections.abc import Iterator

import pytest  # 第三方测试库。对照 JUnit。夹具、断言改写都由它在收集测试时处理。


@pytest.fixture
def box() -> Iterator[list[str]]:
    """每个测试一个新列表。默认 scope 就是 function。

    @pytest.fixture 是装饰器：不改变你调用函数的写法，而是给 pytest 做标记。
    对照在方法上加 @BeforeEach。测试函数不会自己写 box()。参数名写成 box，pytest 就来调这个函数。
    按名字对接，不是按类型。两个夹具都返回 list[str] 时，Python 不会像 Spring 那样按类型选一个。
    """

    data: list[str] = []  # 冒号是类型标注。[] 是一个新的空列表。对照 new ArrayList<String>()。
    yield data  # 把这个列表交给测试。yield 之后函数先停住。对照把准备好的对象交给测试方法，测试跑完再回到下面。
    # 测试结束（通过或断言失败）pytest 都会回到这一行。clear() 是列表的方法，把元素删光，列表对象还在。
    # 对照 list.clear()。下一份测试不会看见它，因为下一份是新列表，不是因为这里清空了。
    data.clear()  # 清理这一份。下一份测试不会看见它，因为下一份是新列表。


@pytest.fixture(scope="module")
def shared() -> list[str]:
    """整个文件只造一次。后面的测试能看见前面测试放进去的东西。

    scope="module" 是关键字参数，告诉 pytest：这个文件里只调用一次。对照 @BeforeAll 造一份、所有测试共用。
    这里用 return，没有 yield。没有「测试结束之后还要跑的清理」。返回的那一个列表会一直留到文件里的测试都跑完。
    """

    return []  # 每次调用这个函数都会 new 一个空列表。因为 scope 是 module，pytest 只会调用一次。


def test_box_first(box: list[str]) -> None:
    # 参数名 box 必须和上面的夹具函数同名。pytest 把 yield 出去的那个列表填进来。你不要自己 box()。
    # append 在列表末尾加一个元素，改的是这一个列表对象。对照 list.add("a")。
    box.append("a")
    # assert 是语句，不是方法。条件为假就抛 AssertionError，这个测试算失败。对照 assertEquals。
    # pytest 会改写 assert，失败时打印两边的值。python -O 会丢掉 assert，所以跑测试不要加 -O。
    # == 对列表是按顺序比每个元素，不是问是不是同一个对象。对照 equals，不是 ==。
    assert box == ["a"]


def test_box_second(box: list[str]) -> None:
    # 如果这是 module 作用域，这里会看见 ["a"]，断言失败。
    # 默认每个测试重新调用 box()，所以这是另一个空列表。上一个测试的 append 不在这里。
    assert box == []


def test_shared_first(shared: list[str]) -> None:
    shared.append("a")  # 加进那份整个文件共用的列表。
    assert shared == ["a"]


def test_shared_second(shared: list[str]) -> None:
    # 同一个列表。上一个测试放进去的 "a" 还在。
    # 没有再 append。如果 shared 是 function 作用域，这里会是 []，断言会失败。
    assert shared == ["a"]
