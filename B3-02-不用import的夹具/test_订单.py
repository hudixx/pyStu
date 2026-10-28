"""测试文件不导入 conftest。参数名 buyer 和夹具函数名一样，pytest 会接上。

本文件没有 import conftest，也没有 import pytest。assert 是 Python 自带的语句，不需要从 pytest 导入。
pytest 只是在跑测试时把失败的 assert 显示得更清楚。
"""

from __future__ import annotations


def test_buyer(buyer: str) -> None:
    # 参数名 buyer 是关键。pytest 在同目录的 conftest.py 里找到叫 buyer 的夹具，调用它，把返回值填进来。
    # 对照按名字注入，不是按类型。你把参数改名叫 name，即使类型还是 str，也接不上，收集测试时就会报错。
    # 不要在这里写 from conftest import buyer。那样拿到的是函数，还要自己 buyer() 才得到字符串。
    assert buyer == "hudi"  # == 对字符串比的是内容。对照 equals。条件为假就抛 AssertionError，本测试失败。
