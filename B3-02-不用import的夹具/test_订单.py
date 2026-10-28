"""测试文件不导入 conftest。参数名 buyer 和夹具函数名一样，pytest 会接上。"""

from __future__ import annotations


def test_buyer(buyer: str) -> None:
    assert buyer == "hudi"
