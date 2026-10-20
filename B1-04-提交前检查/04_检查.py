"""选修 B1 第 4 课：提交前跑 ruff 和 mypy。不过就不要提交。

第 25 课是会敲这两条命令。这一课把它们当成门：退出码不是 0，这扇门就没过。
检查器不执行业务代码。坏例子写在临时文件里，不留在仓库。
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# 故意写错的一份。它是字符串，不是这个文件里的代码，mypy 不会检查这几行。
# unused 让 ruff 报 F841。add("a", "b") 运行时能拼成 "ab"，mypy 仍说类型不对。
BAD = """
def add(a: int, b: int) -> int:
    return a + b

def main() -> None:
    unused = 1
    add("a", "b")
"""


def check(path: Path) -> tuple[int, int]:
    """返回 ruff 和 mypy 的退出码。0 是过。检查器只读文件，不调用 main。"""

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return ruff.returncode, mypy.returncode


def main() -> None:
    here = Path(__file__).resolve()
    good_ruff, good_mypy = check(here)
    print("本文件 ruff", good_ruff)
    print("本文件 mypy", good_mypy)

    # mkstemp 在系统临时目录造文件。不要把坏例子留在课目录，否则以后扫整个仓库会一直红。
    fd, name = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    bad_path = Path(name)
    try:
        bad_path.write_text(BAD, encoding="utf-8")
        bad_ruff, bad_mypy = check(bad_path)
    finally:
        bad_path.unlink(missing_ok=True)
    print("坏例子 ruff", bad_ruff)
    print("坏例子 mypy", bad_mypy)


if __name__ == "__main__":
    main()
