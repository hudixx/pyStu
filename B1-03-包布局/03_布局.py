"""选修 B1 第 3 课：库代码放在 src 下，课目录本身不是包。

对照 Maven 的 src/main/java。仓库根上还有文档和练习，那些不该被 import。
这门课现有的「50-会话与一张表」这种目录名有横线，也不能当包名。这里不改那些目录。
"""

from __future__ import annotations

import sys  # sys.path 是模块搜索路径，对照 classpath。import 时按这个列表逐个目录找。
from pathlib import Path  # 面向对象的路径。对照 java.nio.file.Path。用 / 拼接，不用自己拼反斜杠。

# 插入必须写在 import handbook 之前。已经失败过的 import 不会因为后来改了路径就重试。
# 插到开头，避免撞上已经安装的同名包。
# __file__ 是本 .py 的路径。resolve() 变成绝对路径，顺手去掉 ..。parent 是所在文件夹，也就是「B1-03-包布局」。
# / "src" 拼出子目录。这是 Path 的运算，不是除法。对照 Paths.get(dir, "src")。
SRC = Path(__file__).resolve().parent / "src"
# insert(0, ...) 插到列表最前。str(SRC) 把 Path 变成普通字符串，因为 sys.path 里要的是 str。
# 对照把某个目录临时加到 classpath 的最前面。
sys.path.insert(0, str(SRC))

# 从包 handbook 的模块 refund 里取出 days 和 phone 两个函数。对照 import static，但这里取出的是函数对象。
# 包名 handbook 对应 src/handbook/ 这个目录。目录名能当包名，是因为它是合法标识符：字母开头，没有横线。
# noqa: E402 是给 ruff 看的：E402 这条规则说「import 必须写在文件顶部」。这里故意写在改完 sys.path 之后，所以让它别报。
# 这个注释必须留在这一行末尾。挪走的话，检查器又会认为这行违规。
from handbook.refund import days, phone  # noqa: E402  # 路径放好之后才能导入。


def main() -> None:
    # days 和 phone 是函数。加上括号才调用。不加括号得到的是函数本身，print 会打出函数的地址，不是 7。
    # 对照要写 days()，不是把方法引用当返回值打印。数字和电话来自包，不是写在这个脚本里的字面量。
    print(days(), phone())


# 直接运行本文件才进 main。被 import 时不打印。
if __name__ == "__main__":
    main()
