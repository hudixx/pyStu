"""第 17 课参考答案。题 1 / 2 你已经做对。

model_dump() 得到 Python dict（done 是 False）。
json.dumps / model_dump_json 得到 JSON 文本（done 是 false，没有引号的布尔）。
空 title 被 Field(min_length=1) 拦住，e.errors()[0]["msg"] 即第一条人话。

题 3：pydantic 构造 UserIn(years="1") 能把字符串变成 int。
这和普通注解 def f(years: int) 有什么不同？更像 Jackson 还是纯类型提示？

普通注解运行时不检查、也不转换：f("1") 能跑，years 仍是 str。
pydantic 在构造那一行就校验：能转就转（"1" → int 1），不能转或越界就
ValidationError，拿不到半残对象。所以更像 Jackson + Bean Validation
（反序列化时转类型、@Valid 失败就拒），不像纯类型提示（只给 IDE / mypy 看）。
FastAPI 下一课靠这个：请求体对不上自动 422，进不了你的函数。
"""

from pydantic import BaseModel, Field, ValidationError


class TodoIn(BaseModel):
    title: str = Field(min_length=1)
    done: bool = False


def main() -> None:
    dto = TodoIn(title="买牛奶")
    print(dto.model_dump())  # {'title': '买牛奶', 'done': False}

    try:
        TodoIn(title="")
    except ValidationError as e:
        print(e.errors()[0]["msg"])


if __name__ == "__main__":
    main()
