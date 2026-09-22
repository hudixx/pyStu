

def city_of(user: dict, default: str = "未知") -> str:
    return user.get("city", default)

def main() -> None:
    #
    s = "JavaDeveloper"
    print(s[0:4])
    print(s[-9:])
    print(s[::2])

    """
        a = ["java", "python", "go"]
        c = ["java", "python", "rust"]
    """
    a = ["java", "python"]
    b = a
    c = a[:]
    b.append("go")
    c.append("rust")
    print(a) # ["java", "python", "go"]
    print(c) # ["java", "python", "rust"]

    # dict便利
    user = {
        "name": "hudi",
        "city": "上海",
        "age": 18,
    }

    for k, v in user.items():
        print(k, v)

    for e in user.items():
        x, y = e
        print(e)
        print(f"{x} + {y}" )

    listitem = [1, 2, 3, 4]

    for item in listitem:
        print(item)

    print(city_of({"name": "hudi", "city": "上海"}))
    print(city_of({"name": "hudi"}))

if __name__ == "__main__":
    main()





"""
    空集合必须是set() 不能写{} 。因为{} 是dict
"""

