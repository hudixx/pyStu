"""示例模块：一个 .py 文件就是一个模块。

对照 Java：这相当于一个叫 greet 的类文件，但没有强制 class。
其它文件用 import greet 就能调用这里的函数。
"""


def hello(name: str) -> str:
    """返回一句问候。被 import 时这段 def 会执行（定义函数），
    但不会自动调用，除非下面有模块级代码。
    """
    return f"你好, {name}"


# 模块被 import 时，这里的 print 也会跑一次。
# 所以「有副作用的代码」不要直接写在模块顶层，请放到 main 里。
print(f"[greet.py 被加载] __name__ = {__name__}")


if __name__ == "__main__":
    # 直接运行 python greet.py 时，__name__ 是 "__main__"
    # 被别人 import 时，__name__ 是 "greet"，不会进这里
    print(hello("直接运行"))
