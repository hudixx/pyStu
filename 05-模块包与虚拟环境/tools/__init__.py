"""tools 包的初始化文件。

有这个文件（哪怕是空的），Python 才把 tools 目录当成包。
Java 对照：目录名就是 package 名，__init__.py 有点像包的门面。

可以在这里转出口径，让调用方写成 from tools import shout。
"""

from tools.text import shout

# 声明「from tools import *」时公开哪些名字。不用 * 也可以不写。
__all__ = ["shout"]
