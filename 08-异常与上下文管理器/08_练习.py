
from pathlib import Path

def parse_int(raw: str) -> None:
    try:
        int(raw)
    except ValueError as e:
        print("失败:", raw)
    else:
        print("成功:", raw)
    finally:
        print("转换结束")

class AgeError(Exception):
    """年龄不合法。类体不能完全空着，写 docstring 或 pass 都行。"""

def set_age(age: int) -> int:
    if age < 0:
        raise AgeError("年龄不能为负")
    # else:   # 不必再写 else，raise 已经结束函数
    return age



def main() -> None:

    #第一题
    parse_int("42")
    parse_int("X")
    #第二题
    try:
        set_age(-1)
    except AgeError as e:
        print(e)
    #第三题
    path = Path(__file__).with_name("note.txt")
    with path.open("w", encoding="utf-8") as f:
        f.write("hudi 学 Python")
    with path.open("r", encoding="utf-8") as f:
        print("读取到:", f.read().strip())
    # path.unlink()
    #第四题 不清楚
    """
     Java 是名义类型：参数类型、throws IOException 都要在签名里声明，
     编译器在跑之前就逼你处理或继续声明。
     文件、网络几乎处处是检查异常，所以 throws 满天飞。

    Python 运行时按结构办事：
        函数签名不声明「会抛什么」，也没有编译器扫 throws。
        出错就 raise，愿意接就 except，不接就冒到顶打印 traceback。
        这和「有 speak 就能当 speaker」一样——契约挪到了运行时。
    """



if __name__ == "__main__":
    main()