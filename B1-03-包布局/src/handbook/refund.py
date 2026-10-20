"""退款这一节。函数在这个模块里，不堆进 __init__.py。"""

from __future__ import annotations


def days() -> int:
    """购买后几天内可以退。"""

    return 7


def phone() -> str:
    """公开的客服电话。这是资料，不是密钥。"""

    return "400-100-1000"
