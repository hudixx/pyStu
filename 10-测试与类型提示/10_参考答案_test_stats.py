"""第 10 课测试参考。你的 5 个用例都能跑通。

漏了一条题目要求：clamp(-5, 0, 10) == 0。
average 期望写 2.0 更贴返回类型 float；assertEqual(2.0, 2) 也能过，因为 == 比的是值。
"""

import unittest

from stats import average, clamp
from textutil import repeat


class TestAverage(unittest.TestCase):
    def test_three_numbers(self) -> None:
        self.assertEqual(average([1, 2, 3]), 2.0)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            average([])


class TestClamp(unittest.TestCase):
    def test_above(self) -> None:
        self.assertEqual(clamp(100, 0, 10), 10)

    def test_below(self) -> None:
        self.assertEqual(clamp(-5, 0, 10), 0)


class TestRepeat(unittest.TestCase):
    def test_repeat(self) -> None:
        self.assertEqual(repeat("ab", 2), "abab")

    def test_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            repeat("ab", -1)


if __name__ == "__main__":
    unittest.main()
