"""选修 B1 第 4 课参考答案。题 1、题 2 都过。题 3 写在下面。选修 B1 结束。

跑出来是：
7 天
ruff 0
mypy 0

练习用 sys.executable 对本文件跑了 ruff 和 mypy，两个退出码都是 0。
没有在仓库里留一份故意不过的 .py，也没有装 git 钩子。

days(7) 打成了 7天，7 和天之间少了一个空格。题目要的是 7 天。
n == 7 走这一支、否则走「不知道」，这个分支是对的。

题 3：
- 这扇门不是 pytest。
  ruff 和 mypy 只读文件，不调用 days(7)。
  pytest 才会真的执行函数，看返回值是不是「7 天」。
  这扇门拦的是未使用的变量、写错的名字、注解对不上。
  它不证明那几个字对。检查过了还要测试。测试过了也不能代替检查。
- 类型对不上时，不能先写 # type: ignore。
  ignore 是把报错藏起来，不是把类型改对。mypy 不再说，问题还在。
  它留给第三方库的注解是烂的、你改不了那份代码的时候。
  自己的函数先改参数、改返回值，或者改调用。
  一上来 ignore，这扇门就形同虚设。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def days(n: int) -> str:
    """7 的时候返回「7 天」。注意 7 和天之间有一个空格。"""

    if n == 7:
        return "7 天"
    return "不知道"


def main() -> None:
    print(days(7))
    here = Path(__file__).resolve()
    # sys.executable 是当前这个解释器。不要写死别的机器上的 python 路径。
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(here)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", str(here)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    # 检查器只读这个文件，不会为了打分去调用 days。0 是过。
    print("ruff", ruff.returncode)
    print("mypy", mypy.returncode)


if __name__ == "__main__":
    main()
