"""退款这一节。函数在这个模块里，不堆进 __init__.py。

文件名 refund.py 去掉 .py 就是模块名。外面写 from handbook.refund import days。
对照一个类里的静态方法，但这里没有类，函数直接放在模块上。
"""

from __future__ import annotations


def days() -> int:
    """购买后几天内可以退。

    -> int 对照返回 int。解释器不检查。真返回了一个字符串的话，要等 mypy 或调用方出错才知道。
    """

    return 7  # return 把值交回调用方。不写 return，函数结果是 None，对照返回 null，不是 0。


def phone() -> str:
    """公开的客服电话。这是资料，不是密钥。"""

    return "400-100-1000"  # 字符串用引号。返回的是这段文字本身，不是变量名。
