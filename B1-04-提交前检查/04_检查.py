"""选修 B1 第 4 课：提交前跑 ruff 和 mypy。不过就不要提交。

第 25 课是会敲这两条命令。这一课把它们当成门：退出码不是 0，这扇门就没过。
检查器不执行业务代码。坏例子写在临时文件里，不留在仓库。

对照：ruff 像 Checkstyle，看风格和明显的错误。mypy 像 javac 的类型检查，但不替你运行程序。
退出码是进程结束时交给操作系统的整数。0 表示过，非 0 表示没过。对照 System.exit 的那个数。
"""

from __future__ import annotations

import os  # os.close：关掉一个文件描述符。mkstemp 打开了文件，不用就得关，否则占着句柄。
import subprocess  # 启动另一个进程。对照 ProcessBuilder。这里用来跑 ruff 和 mypy。
import sys  # sys.executable 是当前这个 python 解释器的路径。用它，而不是写死 python 两个字。
import tempfile  # 在系统临时目录造文件。对照 Files.createTempFile，但返回值多一个文件描述符。
from pathlib import Path  # 路径对象。write_text、unlink 都在它上面。对照 java.nio.file.Path。

# 故意写错的一份。它是字符串，不是这个文件里的代码，mypy 不会检查这几行。
# 三引号字符串可以跨行。变量 BAD 的值就是下面这几行文本，解释器不会去执行里面的 def。
# unused 让 ruff 报 F841（变量赋了值却没用）。add("a", "b") 运行时能拼成 "ab"，mypy 仍说类型不对。
# 这就是「检查器不运行代码」：真跑起来 "a"+"b" 是合法的，类型标注却说两个参数必须是 int。
BAD = """
def add(a: int, b: int) -> int:
    return a + b

def main() -> None:
    unused = 1
    add("a", "b")
"""


def check(path: Path) -> tuple[int, int]:
    """返回 ruff 和 mypy 的退出码。0 是过。检查器只读文件，不调用 main。

    -> tuple[int, int] 对照返回一个 Pair。调用方用 a, b = check(path) 拆开。
    """

    ruff = subprocess.run(
        # 列表里每个元素是一个参数，不是一整句 shell。对照 ProcessBuilder("python", "-m", "ruff", ...)。
        # 不要拼成一个大字符串再交给 shell，路径里有空格也不会被拆错。
        # sys.executable：本进程的 python.exe。-m ruff：用这个解释器把 ruff 当模块跑，不依赖你有没有把 ruff 加进 PATH。
        # check 是 ruff 的子命令。str(path) 把 Path 变成字符串，子进程认的是路径文字。
        [sys.executable, "-m", "ruff", "check", str(path)],
        capture_output=True,  # 把子进程的 stdout、stderr 接住，不打到你的控制台。对照重定向到管道。
        text=True,  # 把输出从 bytes 解码成 str。不写的话，.stdout 是字节，打印会带 b'...'。
        encoding="utf-8",  # 按 UTF-8 解码。不写时 Windows 可能按 GBK 解，中文报错信息会乱。
    )
    mypy = subprocess.run(
        # 同一套参数。mypy 没有 "check" 这个子命令，路径直接跟在 -m mypy 后面。
        [sys.executable, "-m", "mypy", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    # returncode 是退出码。0 过，非 0 没过。对照 process.exitValue()。run 会等进程结束才返回。
    return ruff.returncode, mypy.returncode


def main() -> None:
    # __file__ 是本 .py。resolve() 变成绝对路径。检查器要的是文件路径，不是文件内容。
    here = Path(__file__).resolve()
    # 拆开 check 返回的两个整数。对照一次拿到 Pair 的左右两边。
    good_ruff, good_mypy = check(here)
    print("本文件 ruff", good_ruff)  # 本文件应是 0。上面的 BAD 只是字符串，ruff 不把它当代码。
    print("本文件 mypy", good_mypy)

    # mkstemp 在系统临时目录造文件。不要把坏例子留在课目录，否则以后扫整个仓库会一直红。
    # 返回两个值：fd 是操作系统的文件描述符（一个整数，文件已经打开），name 是路径字符串。
    # suffix=".py" 让文件名以 .py 结尾。ruff 和 mypy 靠这个后缀认出它是 Python。
    fd, name = tempfile.mkstemp(suffix=".py")
    os.close(fd)  # 我们不用这个已打开的句柄，马上关掉。不关的话，Windows 上后面可能删不掉这个文件。
    bad_path = Path(name)  # 把字符串路径包成 Path，才能用 write_text 和 unlink。
    try:
        # write_text 一次把整个字符串写进文件。encoding 写明 utf-8。对照 Files.writeString。
        bad_path.write_text(BAD, encoding="utf-8")
        bad_ruff, bad_mypy = check(bad_path)  # 检查的是临时文件，不是本文件。两个退出码都应该不是 0。
    finally:
        # unlink 删除文件。对照 Files.delete。missing_ok=True：文件已经不在也不抛异常。对照 deleteIfExists。
        # 放在 finally 里：检查器即使抛了，坏例子也不留在临时目录。
        bad_path.unlink(missing_ok=True)
    print("坏例子 ruff", bad_ruff)  # 非 0。unused 没被使用。
    print("坏例子 mypy", bad_mypy)  # 非 0。add 的参数标注是 int，调用时给了 str。


if __name__ == "__main__":
    main()
