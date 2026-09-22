import unittest
from stats import average, clamp
from textutil import repeat

class TestStats(unittest.TestCase):
    def test_average(self) -> None:
        self.assertEqual(average([1, 2, 3]), 2)

    def test_average_empty(self) -> None:
        with self.assertRaises(ValueError):
            average([])

    def test_clamp(self) -> None:
        self.assertEqual(clamp(100, 0, 10), 10)

    def test_repeat(self) -> None:
        self.assertEqual(repeat("ab", 2), "abab")
    def test_repeat_err(self) -> None:
        with self.assertRaises(ValueError):
            repeat("ab", -1)

if __name__ == '__main__':
    unittest.main()