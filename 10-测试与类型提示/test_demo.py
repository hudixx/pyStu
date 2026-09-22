"""第 10 课示例测试。在本目录运行：

    PYTHONUTF8=1 python -m unittest test_demo.py -v
"""

import unittest

from stats import average, clamp


class TestAverage(unittest.TestCase):
    """对照 JUnit 的 @Test 方法。"""

    def test_two_numbers(self) -> None:
        self.assertEqual(average([2, 4]), 3.0)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            average([])


class TestClamp(unittest.TestCase):
    def test_inside(self) -> None:
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_below(self) -> None:
        self.assertEqual(clamp(-1, 0, 10), 0)

    def test_bad_range(self) -> None:
        with self.assertRaises(ValueError):
            clamp(1, 10, 0)


if __name__ == "__main__":
    unittest.main()
