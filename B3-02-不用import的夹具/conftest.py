"""选修 B3 第 2 课：这个目录里的测试不用 import 就能拿到夹具。

文件名必须是 conftest.py。pytest 会自己加载它。
对照测试基类或 @TestConfiguration：放在这个目录，子目录里的测试也能看见。
不要把这种文件放到仓库根上，否则所有课的测试都会看见这些夹具。
"""

from __future__ import annotations

import pytest


@pytest.fixture
def buyer() -> str:
    """购买人。测试函数的参数名写成 buyer，就会拿到这份值。"""

    return "hudi"
