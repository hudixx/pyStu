"""第 07 课参考答案。继承、鸭子类型、isinstance 你都写对了。

summary 里题目用的是中文逗号「，」，你写的是英文逗号「,」，不影响机制。
FileLogger 题目希望前缀是 [file]，你写成了 file-，同样不影响鸭子类型本身。
"""

from typing import override


class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name
        self.salary = salary

    def summary(self) -> str:
        return f"{self.name} 薪资 {self.salary}"


class Manager(Employee):
    def __init__(self, name: str, salary: int, dept: str) -> None:
        super().__init__(name, salary)
        self.dept = dept

    @override
    def summary(self) -> str:
        return f"{self.name} 主管 {self.dept}，薪资 {self.salary}"


class FileLogger:
    def write(self, msg: str) -> None:
        print(f"[file] {msg}")


class ConsoleLogger:
    def write(self, msg: str) -> None:
        print(msg)


def record(logger, msg: str) -> None:
    logger.write(msg)


def main() -> None:
    mgr = Manager("hudi", 20000, "平台")
    print(mgr.summary())
    record(FileLogger(), "日志信息")
    record(ConsoleLogger(), "日志信息")
    print(isinstance(mgr, Manager))    # True
    print(isinstance(mgr, Employee))   # True，和 Java 的 instanceof 一样


if __name__ == "__main__":
    main()
