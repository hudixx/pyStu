
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
        return f"{self.name} 主管 {self.dept}, 薪资 {self.salary}"

class FileLogger:
    def __init__(self, file: str) -> None:
        self.file = file

    def write(self, msg: str) -> None:
        print(f"{self.file}-{msg}")

class ConsoleLogger:
    def write(self, msg: str) -> None:
        print(msg)

def record(logger, msg: str) -> None:
    logger.write(msg)




def main() -> None:
    #第一题
    manager = Manager("hudi" , 20000, "平台")
    print(manager.summary())
    #第二题
    record(FileLogger("file"), "日志信息")
    record(ConsoleLogger(), "日志信息")
    #第三题 两个都是true. Java 的 mgr instanceof Employee 同样是 True
    print(isinstance(manager, Manager))
    print(isinstance(manager, Employee))
    #第四题
    """ 
    Java 是名义类型（nominal）。
        参数必须写成某个类型：void greet(Speaker s)。能传进去的，只能是 声明了 implements Speaker 的类。两个类碰巧都有 speak()，没有共同接口，编译器照样拒绝。所以 interface
        几乎是刚需：它既是编译期契约，也是多态的入场券。
        
    Python 运行时是结构类型（鸭子类型）。
        greet(speaker) 不要求你声明 speaker 是什么。真正执行到 speaker.speak() 时，只问一件事：这个对象上有没有 speak。有就调，没有就 AttributeError。共同父类、interface、implements 都不是运行所必需的。
    """
if __name__ == "__main__":
    main()