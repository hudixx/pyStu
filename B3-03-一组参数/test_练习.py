from __future__ import annotations
import pytest


def days(n: int) -> str:
    return "7 天" if n == 7 else "不知道"

@pytest.mark.parametrize(
    ("n", "text"),
    [
        (7, "7 天"),
        (0, "不知道"),
        (8, "不知道")
    ]
)
def test_days(n, text) -> None:
    assert days(n) == text

#  题2不知道，请在参考答案的注释中个给出