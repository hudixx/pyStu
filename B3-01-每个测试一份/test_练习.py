from __future__ import annotations

import pytest

@pytest.fixture
def box() -> list[str]:
    return []

def test_box_first(box: list[str]) -> None:
    box.append("a")
    assert len(box) == 1


def test_box_second(box: list[str]) -> None:
    box.append("b")
    assert len(box) == 1

#  题2不知道，请在参考答案的注释中个给出