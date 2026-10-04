from typing import Literal


def label(source: int) -> Literal["bad","ok","good"]:
    if source < 60:
        return "bad"
    elif  source < 80:
        return "ok"
    else:
        return "good"


def main() -> None:
    print(label(42))
    print(label(70))
    print(label(95))


if __name__ == "__main__":
    main()

"""

题一: 
    python -m ruff check 25_练习.py
        All checks passed!
        
    python -m mypy  25_练习.py
       Success: no issues found in 1 source file

题二：
    请在参考答案的注释只能给出


"""