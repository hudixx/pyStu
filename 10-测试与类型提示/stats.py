"""给第 10 课练习准备的被测模块。练习里不要改这个文件，只写测试。"""


def average(nums: list[int]) -> float:
    """返回整数列表的平均值。空列表抛 ValueError。"""
    if not nums:
        raise ValueError("空列表没有平均值")
    return sum(nums) / len(nums)


def clamp(n: int, lo: int, hi: int) -> int:
    """把 n 限制在 [lo, hi] 闭区间内。"""
    if lo > hi:
        raise ValueError("lo 不能大于 hi")
    if n < lo:
        return lo
    if n > hi:
        return hi
    return n
