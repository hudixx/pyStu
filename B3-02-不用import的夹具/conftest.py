"""选修 B3 第 2 课：这个目录里的测试不用 import 就能拿到夹具。

文件名必须是 conftest.py。pytest 会自己加载它。
对照测试基类或 @TestConfiguration：放在这个目录，子目录里的测试也能看见。
不要把这种文件放到仓库根上，否则所有课的测试都会看见这些夹具。

这不是 Python 的语法。普通 import 不会因为旁边有个 conftest.py 就自动拿到 buyer。
只有 pytest 收集这个目录里的测试时，才会先执行本文件，再按参数名把夹具填进测试函数。
"""

from __future__ import annotations

import pytest


@pytest.fixture
def buyer() -> str:
    """购买人。测试函数的参数名写成 buyer，就会拿到这份值。

    返回 str。没有 yield，所以没有「测试结束之后再清理」的后半段。
    默认 scope 是 function：每个测试都会再调用一次这个函数。这里每次都返回同一个字面量 "hudi"，看不出差别。
    """

    return "hudi"  # 测试里的 buyer 参数就是这个字符串。不是函数本身。
