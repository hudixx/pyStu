
name: str = "hudi"
years: int = 30
label_value = 111

def introduce(name: str, years: int) -> str:
    return f"我是 {name}, 学编程 {years} 年。"

def label(value) -> str:
    if value:
       return "有内容"
    else:
        return "空"



def main() -> None:
    print(introduce(name, years))
    print(label(label_value))

if __name__ == "__main__":
    main()