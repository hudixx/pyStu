""" 测试"""


from pathlib import Path
import sys

_file =  Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(_file))

from notes.phone import hotline


def main() -> None:
    print(hotline())

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出