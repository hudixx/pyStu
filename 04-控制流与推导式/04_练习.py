
def sign_of(n: int) -> str:
    return "正" if n > 0 else "非正"

def test02(*args) -> None:
    for index, arg in enumerate(args, start = 1):
        print(f"{index}. {arg}")

def test03(*args) -> list:
    return [x * x for x in args if x % 2 == 0]

def temp1(*args) -> None:
    for index, arg in enumerate(args):
        if arg == 9:
            print("第", index +1, "轮找到: " , arg)
            break
        elif arg % 2 == 0:
            print("第", index +1, "轮为偶数， 值为： ", arg)
            # break
        else :
            print("第", index +1, "的值为：", arg)
    else :
        print("进入break")

def main() -> None:
    #第1题
    print(sign_of(3))
    print(sign_of(0))
    #第2题
    langs =  ["java", "python", "go"]
    test02(*langs)
    #第3题
    nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print(test03(*nums))
    temp = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    temp1(*temp)
    #第4题
    """
    Python 的列表推导式，对应 Java Stream 的map 和 filter
    for/else 里的 else，在for循环里面全程没被break时
    """

if __name__ == "__main__":
    main()