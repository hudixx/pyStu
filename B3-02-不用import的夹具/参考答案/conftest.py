"""选修 B3 第 2 课参考答案里的夹具。

文件名必须是 conftest.py。pytest 收集这个目录时会自己执行它。
测试文件不要 import 本文件。参数名写成 phone，才会拿到返回值。
"""

from __future__ import annotations

import pytest


@pytest.fixture
def phone() -> str:
    """热线号码。测试函数的参数名写成 phone，就会拿到这串字。

    返回 str。没有 yield，所以没有测试结束之后再清理的后半段。
    默认 scope 是 function。这里每次都返回同一个字面量，看不出「每个测试一份」的差别。
    """

    return "400-100-1000"
