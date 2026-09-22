"""第 02 课示例：str / list / tuple / dict / set。

建议对照 Java 的 String、ArrayList、HashMap、HashSet 边跑边看。
每个 print 前面的注释写了「你应该看到什么」。
"""

from __future__ import annotations  # 让 list[int] 这种注解在所有写法下都更省心


def demo_str() -> None:
    """字符串：不可变，切片含头不含尾。"""
    s = "Python"
    print("=== str ===")
    print(s[0])       # P；没有 char 类型，结果仍是长度为 1 的 str
    print(s[-1])      # n；-1 是最后一个字符
    print(s[0:3])     # Pyt；结束下标 3 不包含
    print("th" in s)  # True；in 相当于 contains
    print("-".join(["a", "b", "c"]))  # a-b-c；join 由分隔符来调用


def demo_list_and_alias() -> None:
    """list 可变；b = a 是别名，不是拷贝。"""
    print("=== list 与引用 ===")
    a = [1, 2, 3]
    b = a            # 两个名字指向同一个 list 对象
    b.append(4)
    print(a)         # [1, 2, 3, 4]；改 b 就是改 a

    c = a[:]         # 切片拷贝：新 list，元素还是原来那些对象（浅拷贝）
    c.append(5)
    print(a)         # [1, 2, 3, 4]；a 不再跟着变
    print(c)         # [1, 2, 3, 4, 5]


def demo_tuple() -> None:
    """tuple 不可变，适合打包、多返回值。"""
    print("=== tuple ===")
    point = (3, 4)
    x, y = point     # 解包：左边几个名字，右边就要几个值
    print(x, y)      # 3 4

    one = (1,)       # 单元素 tuple 必须有逗号
    not_tuple = (1)  # 这只是整数 1，括号被当成运算优先级
    print(type(one), type(not_tuple))


def demo_dict() -> None:
    """dict 类似 HashMap；[] 取值缺 key 会炸，get 不会。"""
    print("=== dict ===")
    user: dict[str, str | int] = {"name": "hudi", "years": 30}
    print(user["name"])                 # hudi
    print(user.get("city"))             # None；没有 city 这个 key
    print(user.get("city", "未知"))     # 未知；类似 getOrDefault
    user["city"] = "上海"
    print("name" in user)               # True；in 对 dict 只判断 key

    for key, value in user.items():
        print(f"{key}={value}")


def demo_set() -> None:
    """set 去重；{} 是空 dict，空集合必须写 set()。"""
    print("=== set ===")
    tags = {"python", "java", "python"}
    print(tags)              # 重复的 python 只留一份；打印顺序不必纠结
    print("java" in tags)    # True
    print(set() , {})        # set() 是空集合；{} 是空字典


def demo_eq_vs_is() -> None:
    """== 比内容（equals），is 比身份（Java 的 == 用在对象上）。"""
    print("=== == 与 is ===")
    a = [1, 2]
    b = [1, 2]
    print(a == b)    # True
    print(a is b)    # False
    print(None is None)  # True；None 是单例，判断空值请用 is None


def main() -> None:
    demo_str()
    demo_list_and_alias()
    demo_tuple()
    demo_dict()
    demo_set()
    demo_eq_vs_is()


if __name__ == "__main__":
    main()
