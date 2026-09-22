"""第 03 课示例：默认参数、*args、引用传递、作用域。

对照 Java：
- 没有方法重载，靠默认参数
- 可变默认值只创建一次（Java 每次进方法 new 一次，这里刚好相反）
- if / for 没有块级作用域
"""

from __future__ import annotations


def greet(name: str = "陌生人") -> str:
    """默认参数代替 Java 的两份 greet() 重载。"""
    return f"你好, {name}"


def add_item_wrong(item: str, bucket: list[str] = []) -> list[str]:
    """反例：默认 list 在 def 时就建好了，所有调用共享这一张表。

    千万别在生产代码里这么写。这里只为了让你亲眼看见串数据。
    """
    bucket.append(item)
    return bucket


def add_item(item: str, bucket: list[str] | None = None) -> list[str]:
    """正例：默认 None，每次需要时再新建 list。"""
    if bucket is None:  # 用 is None，不要用 == None
        bucket = []
    bucket.append(item)
    return bucket


def log_all(*args: object) -> None:
    """*args 相当于 Java 的 String... / Object...，类型是 tuple。"""
    print("args 的类型:", type(args), "内容:", args)


def connect(host: str, **kwargs: object) -> None:
    """**kwargs 把多余的关键字参数收成 dict。Java 没有同等语法。"""
    port = kwargs.get("port", 3306)
    print(f"连接 {host}:{port}，其它参数={kwargs}")


def append_bang(items: list[str]) -> None:
    """改的是同一个 list 对象，调用方能看见。"""
    items.append("!")


def rebind(items: list[str]) -> None:
    """items = ... 只换了函数里的标签，调用方那张表不动。"""
    items = ["全新"]


def demo_scope() -> None:
    """if / for 不开启新作用域。这和 Java 完全不同。"""
    if True:
        x = 1
    print("if 外面的 x =", x)  # 1，Java 里这里编译都过不了

    for i in range(3):
        pass
    print("for 结束之后 i =", i)  # 2，循环变量泄漏


def main() -> None:
    print("=== 默认参数代替重载 ===")
    print(greet())
    print(greet("hudi"))

    print("=== 可变默认值是坑 ===")
    print(add_item_wrong("java"))    # ['java']
    print(add_item_wrong("python"))  # ['java', 'python'] 第二次调用脏了
    print(add_item("java"))          # ['java']
    print(add_item("python"))        # ['python'] 互不影响

    print("=== *args / **kwargs ===")
    log_all("a", "b", "c")
    connect("localhost", port=5432, timeout=10)

    print("=== 传引用 ===")
    langs = ["java"]
    append_bang(langs)
    print("append 之后:", langs)     # ['java', '!']
    rebind(langs)
    print("rebind 之后:", langs)     # 仍是 ['java', '!']

    print("=== 没有块级作用域 ===")
    demo_scope()

    print("=== 函数当值 ===")
    op = greet  # 函数名本身就是对象
    print(op("Ada"))


if __name__ == "__main__":
    main()
