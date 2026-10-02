import json

from pydantic import BaseModel, Field, ValidationError

# 不能写 from 17_pydantic import UserIn：
# Python 模块名必须是合法标识符（字母或 _ 开头），17_pydantic 以数字开头，解析器在 from 后面期望标识符，
# 却看到字面量 17，直接 SyntaxError。对照 Java：也不能 import com.foo.17Bar。
# sys.path 只影响「去哪找模块」，改不了「名字合不合法」，所以第 16 课那招在这里没用。
# 本课练习自己写 TodoIn 即可，不必导入示例里的 UserIn。
# 若真要加载数字开头的文件，用 importlib 按路径加载（第 20 课 test_hello.py 那套）。



class TodoIn(BaseModel):
    title: str = Field(min_length=1)
    done: bool = False

def main() -> None:
    dto = TodoIn(title="买牛奶")
    print(dto.model_dump())
    temp = json.dumps(dto.model_dump(), indent=2, ensure_ascii=False)
    print(temp)
    print(dto.model_dump_json())

    try:
        TodoIn(title="")
    except ValidationError as e:
        print(e.errors()[0]["msg"])
    """
        第三题不知道，请在参考答案中给出简要解答
    """




if __name__ == '__main__':
    main()