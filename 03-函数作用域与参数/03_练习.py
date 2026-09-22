

def repeat(text: str, times: int = 2) -> str:
    # result = ""
    # for _ in range(times):
    #     result = result + text
    return text * times


def collect(item, box=[]):
    box.append(item)
    return box

# 若想要不叠加
def collect_new(item, box: list[str] | None = None) -> list[str]:
    if box is None:
        box = []
    box.append(item)
    return box


def join_names(*names, sep: str = ",") -> str:
    return sep.join(names)

#第4题
""" 在python里可结束后，还能在外面使用i。 java不行 """

# lambda的使用
join_names_new = lambda *names: "|".join(names)

def main() -> None:
    # 第1题
    print(repeat("go"))
    print(repeat("go", 3))

    # 第2题
    print(collect("a")) # ["a"]
    print(collect("b")) # ["a", "b"] 因为这个入参的box是可变对象直接使用了[] ,创建后直接使用了。
    print(collect_new("a")) # ["a"]
    print(collect_new("b")) # ["b"]

    # 第3题
    print(join_names("hudi", "ada"))
    print(join_names("hudi", "ada" , sep = " | "))
    print(join_names_new("a", "b", "c"))

    #第4题
    """ 
        在python里可结束后，还能在外面使用i。 java不行 
        Python 没有块级作用域，for 不开启新一层；i 属于当前函数（这里是 main）
    """

if __name__ == "__main__":
    main()
