"""第 17 课示例：pydantic 模型、Field 校验、ValidationError。

对照 Java：
- class UserIn(BaseModel) ≈ 带 Bean Validation 的 DTO / Record
- Field(min_length=...) ≈ @Size / @NotBlank
- Field(ge=..., le=...) ≈ @Min / @Max
- model_dump() ≈ 把对象再变成 Map，方便交给 json
- ValidationError ≈ ConstraintViolationException
- 和「普通类型注解运行时不检查」不同：pydantic 在构造时真的跑校验，还会做类型转换（像 Jackson）
"""

# 类型注解延迟求值。本课模型简单，写上保持和前后课一致。
from __future__ import annotations

# BaseModel：所有 DTO 的基类。继承它才有校验、model_dump、JSON 互转。
# Field：给字段加约束，对照注解打在 Java 字段上。
# ValidationError：校验失败时抛出，里面装着每一条错误。
from pydantic import BaseModel, Field, ValidationError


class UserIn(BaseModel):
    """入参 DTO。对照 Java record / 带 @Valid 的请求体。

    写在类体里的 name: str、years: int 既是字段声明，也是校验契约。
    不是 Java 那种「先声明字段再写 getter」；pydantic 用注解当 schema。
    """

    # min_length=1：空字符串 "" 不过。对照 @NotBlank + @Size(min=1, max=20)。
    name: str = Field(min_length=1, max_length=20)
    # ge=0：greater or equal，years >= 0；le=80：less or equal，years <= 80。
    # 对照 @Min(0) @Max(80)。注意是 ge/le，不是 gt/lt（那是大于/小于，不含等于）。
    years: int = Field(ge=0, le=80)


def main() -> None:
    """演示三条路：通过、类型转换、校验失败。"""
    # 关键字参数构造。对照 new UserIn("hudi", 30) 或 builder。
    # 非法值在这一行就会抛，不会拿到一个「半残对象」。
    ok = UserIn(name="hudi", years=30)
    print("通过:", ok)  # 打印时 pydantic 会给出 UserIn(name='hudi', years=30)
    # model_dump()：模型 → dict。对照把 Bean 转成 Map。后面 json.dumps / FastAPI 都吃这个。
    print("dict:", ok.model_dump())

    # years 声明的是 int，传入字符串 "1" 时，pydantic 会尝试转成 1。
    # 这是 pydantic / Jackson 的行为，不是普通 Python 注解（普通注解运行时不管）。
    # type: ignore 只是堵住类型检查器：静态上看 years 不该是 str，运行时 pydantic 会收。
    coerced = UserIn(name="ada", years="1")  # type: ignore[arg-type]
    # coerced.years 已经是 int 1，type(...) 会打印 <class 'int'>。
    print("类型转换后 years =", coerced.years, type(coerced.years))

    try:
        # name="" 违反 min_length=1；years=-3 违反 ge=0。一次构造可以攒多条错误。
        UserIn(name="", years=-3)
    except ValidationError as e:
        # e.errors() 是 list[dict]，每条有 loc（字段路径）、msg（人话）、type（错误码）。
        # 对照 ConstraintViolation 集合。len 即失败条数，本例应是 2。
        print("校验失败条数:", len(e.errors()))
        for err in e.errors():
            # loc 是元组，例如 ('name',)；msg 例如 "String should have at least 1 character"。
            print(" -", err["loc"], err["msg"])


# 直接运行本文件才进 main；被 FastAPI / 测试 import 时只加载类定义。
if __name__ == "__main__":
    main()
