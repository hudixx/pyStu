"""第 01 课示例：从 Java 开发者视角看 Python 最基本的程序结构。

对照记忆：
- Java 需要 public class + public static void main
- Python 一个 .py 文件本身就可以直接运行
- if __name__ == "__main__" 相当于「仅当本文件作为入口时才执行」
"""

# ---------------------------------------------------------------------------
# 1. 变量：名字是标签，贴在对象上
#    Java: String name = "Ada";
#    Python 不声明类型也能跑；类型注解只是给人和 IDE 看的
# ---------------------------------------------------------------------------
name: str = "Ada"  # 类型注解 : str，运行时默认不强制检查
age: int = 30
pi: float = 3.14
is_active: bool = True  # 注意：True / False / None 首字母必须大写

# None 相当于 Java 的 null，它是一个单例对象
nickname: str | None = None  # str | None 类似 Java 的 @Nullable String


# ---------------------------------------------------------------------------
# 2. 函数：用 def，缩进表示函数体
#    Java: public static int add(int a, int b) { return a + b; }
# ---------------------------------------------------------------------------
def add(a: int, b: int) -> int:
    """返回 a + b。

    三引号字符串写在函数第一行，叫 docstring，类似 Javadoc。
    """
    return a + b  # Python 的 return 和 Java 一样，函数遇到 return 立即结束


def greet(who: str | None) -> None:
    """打印问候语。返回类型 None 相当于 Java 的 void。"""
    # 空字符串 ""、None 在 if 里都算「假」，不必写成 who != null && !who.isEmpty()
    if who:
        print(f"你好, {who}")  # f-string：把表达式嵌进字符串，类似 STR."你好 \{who}"
    else:
        print("你好, 陌生人")


# ---------------------------------------------------------------------------
# 3. 入口：只有直接运行本文件时才执行
#    被其他文件 import 时，__name__ 会变成模块名，不会走进这里
# ---------------------------------------------------------------------------
def main() -> None:
    """程序入口，对应 Java 的 main 方法。"""
    print("=== 01 语法与心智模型 ===")
    print(f"name = {name}, 类型是 {type(name)}")  # type(x) 类似 x.getClass()
    print(f"age  = {age}, 类型是 {type(age)}")
    print(f"1 + 2 = {add(1, 2)}")

    greet(name)
    greet(nickname)  # nickname 是 None，会走「陌生人」分支

    # 重新贴标签：age 原来指向 int，现在指向 str。合法，但生产代码里别这么干
    # age = "三十"
    # print(age)


if __name__ == "__main__":
    main()
