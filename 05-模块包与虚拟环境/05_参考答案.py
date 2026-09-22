"""第 05 课参考答案。你的 05_练习.py / my_util.py 已经做对。

对照留一份，方便以后复习 import 的两种写法。
运行前请先进入本目录，或直接：
    PYTHONUTF8=1 python 05-模块包与虚拟环境/05_练习.py
"""

import my_util
from my_util import repeat as rpt


def main() -> None:
    print(rpt("go"))                 # gogo
    print(my_util.repeat("go", 3))   # gogogo
    # 被 import 时 my_util.__name__ == "my_util"
    # 直接 python my_util.py 时 __name__ == "__main__"


if __name__ == "__main__":
    main()
