"""选修 B1 第 3 课：库代码放在 src 下，课目录本身不是包。

对照 Maven 的 src/main/java。仓库根上还有文档和练习，那些不该被 import。
这门课现有的「50-会话与一张表」这种目录名有横线，也不能当包名。这里不改那些目录。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 插入必须写在 import handbook 之前。已经失败过的 import 不会因为后来改了路径就重试。
# 插到开头，避免撞上已经安装的同名包。
SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

from handbook.refund import days, phone  # noqa: E402  # 路径放好之后才能导入。


def main() -> None:
    # 数字和电话来自包，不是写在这个脚本里的字面量。
    print(days(), phone())


if __name__ == "__main__":
    main()
