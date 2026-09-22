"""第 02 课参考答案。

题 2 / 3 / 4 你已经做对。题 1 错在切片「结束下标不包含」。

JavaDeveloper 下标对照（正数一行、负数一行）：

    J  a  v  a  D  e  v  e  l  o  p  e  r
    0  1  2  3  4  5  6  7  8  9 10 11 12
  -13-12-11-10 -9 -8 -7 -6 -5 -4 -3 -2 -1
"""


def city_of(user: dict, default: str = "未知") -> str:
    """缺 key 时 get 返回 default，不会 KeyError。"""
    return user.get("city", default)


def main() -> None:
    s = "JavaDeveloper"

    # 前 4 个是下标 0,1,2,3。结束写成 4，因为结束位置不包含
    print(s[0:4])     # Java
    # 你写的 [0:5] 会多带一个 D，变成 JavaD

    # 最后 9 个是 Developer。结束省略 = 取到末尾
    print(s[-9:])     # Developer
    # 你写的 [-9:-1] 会把最后一个 r 排除掉，变成 Develope

    # 步长 2：你已经写对
    print(s[::2])     # JvDvlpr

    a = ["java", "python"]
    b = a             # 别名，和 a 指向同一个 list
    c = a[:]          # 浅拷贝，当时的内容是 ["java", "python"]
    b.append("go")    # 改的是 a 那张表
    c.append("rust")  # 改的是拷贝
    print(a)          # ['java', 'python', 'go']
    print(c)          # ['java', 'python', 'rust']

    print(city_of({"name": "hudi", "city": "上海"}))  # 上海
    print(city_of({"name": "hudi"}))                  # 未知


if __name__ == "__main__":
    main()
