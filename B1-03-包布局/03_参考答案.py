"""选修 B1 第 3 课参考答案。题 1 没跑通。题 2 写在下面。

练习里的包是对的：
src/notes/__init__.py 在，src/notes/phone.py 里的 hotline 返回 400-100-1000。
脚本里也没有自己写这串电话。

没跑通是因为路径多下了一层。练习写成了：

    parent / "src" / "notes"

sys.path 的起点就在 src/notes 里面。
from notes.phone 会去找 src/notes/notes/phone.py，那个目录不存在，所以是
ModuleNotFoundError: No module named 'notes'。

文件实际在 src/notes/phone.py。要把 src 放进 sys.path。
包名 notes 才对得上 src 下面的 notes 这个目录。

如果坚持把 src/notes 放进路径，导入就得写成 from phone import hotline。
那样 notes 不再是包名，也不符合这题「把 src 放进去」。

题 2：
- 课目录 B1-03-包布局 不能当成包名。
  包名必须是合法的标识符。这个名字里有横线，横线不能出现在包名里。
  这个目录里还有文档和练习，那些不该被 import。
- pyproject.toml 里的 where = ["src"] 代替的是脚本里的 sys.path.insert。
  pip install -e 把 src 放进导入路径，每个脚本就不用再自己插一次。
  这门课不改成那套布局。现有课目录仍按原来的方式运行。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 放进去的是 src，不是 src/notes。notes 是 src 下面的包。
SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

from notes.phone import hotline  # noqa: E402  # 路径放好之后才能导入。


def main() -> None:
    # 电话来自 notes.phone，不是写在这个脚本里的字面量。
    print(hotline())


if __name__ == "__main__":
    main()
