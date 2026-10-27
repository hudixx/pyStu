from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def days(n: int) -> str:
    return '7天' if n == 7 else '不知道'

def main() -> None:
    print(days(7))
    here = Path(__file__).resolve()
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(here)],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", str(here)],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    print("ruff", ruff.returncode)
    print("mypy", mypy.returncode)

if __name__ == "__main__":
    main()


#  题3不知道，请在参考答案的注释中个给出