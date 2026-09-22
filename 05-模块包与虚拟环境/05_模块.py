"""第 05 课示例：import、包、__name__。

请在本目录下运行，这样 Python 才能找到旁边的 greet.py 和 tools/：

    cd 05-模块包与虚拟环境
    PYTHONUTF8=1 python 05_模块.py

对照 Java：
- import greet          ≈ import greet.Hello 之后用类名调用
- from greet import hello  ≈ import static，直接用方法名
- tools 目录            ≈ package
"""

import greet                     # 加载 greet.py，模块里顶层代码会执行
from greet import hello as hi    # 只引入函数，并起别名
from tools import shout          # 走 tools/__init__.py 转出的 shout


def main() -> None:
    print("=== 模块 import ===")
    print(greet.hello("hudi"))   # 模块名.函数名
    print(hi("ada"))             # 别名，不必再写 greet.

    print("=== 包 import ===")
    print(shout("python"))       # PYTHON!

    print("=== 当前文件自己的 __name__ ===")
    print(__name__)              # 直接运行时是 __main__


if __name__ == "__main__":
    main()
