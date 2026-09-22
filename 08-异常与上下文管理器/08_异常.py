"""第 08 课示例：try/except/else/finally、raise、with。

对照 Java：
- 没有检查异常，不用在签名上写 throws
- raise ≈ throw
- with ≈ try-with-resources
"""

from pathlib import Path


class BalanceError(Exception):
    """余额不足。自己的业务异常，继承 Exception。"""


class Account:
    def __init__(self, owner: str, balance: int) -> None:
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount: int) -> None:
        if amount > self.balance:
            raise BalanceError(f"{self.owner} 余额不足")
        self.balance -= amount


class DemoCloser:
    """最小上下文管理器：进入时打开，离开时关闭。"""

    def __enter__(self) -> str:
        print("enter: 打开资源")
        return "资源句柄"  # 这个返回值会赋给 with ... as 后面的名字

    def __exit__(self, exc_type, exc, tb) -> bool:
        # exc_type 为 None 表示 with 块里没出错
        print(f"exit: 关闭资源, 有没有异常={exc_type is not None}")
        return False  # 不吞异常


def demo_try() -> None:
    print("=== try / except / else / finally ===")
    raw = "12"
    try:
        n = int(raw)
    except ValueError as e:
        print("转换失败:", e)
    else:
        print("转换成功:", n)  # 没异常才走这里
    finally:
        print("finally 一定执行")


def demo_raise() -> None:
    print("=== 业务异常 ===")
    acc = Account("hudi", 100)
    try:
        acc.withdraw(200)
    except BalanceError as e:
        print("捕获到:", e)


def demo_with() -> None:
    print("=== with 自己写的上下文管理器 ===")
    with DemoCloser() as handle:
        print("使用", handle)

    print("=== with 写文件（对标 try-with-resources）===")
    path = Path(__file__).with_name("demo_out.txt")
    with path.open("w", encoding="utf-8") as f:
        f.write("hello python\n")
    # 离开 with 后文件已关闭，可以再读
    with path.open("r", encoding="utf-8") as f:
        print("读到:", f.read().strip())
    path.unlink()  # 用完删掉演示文件


def main() -> None:
    demo_try()
    demo_raise()
    demo_with()


if __name__ == "__main__":
    main()
