"""第 17 课示例：pydantic 模型、Field 校验、ValidationError。"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class UserIn(BaseModel):
    """入参 DTO。ge=0 表示 years >= 0。"""

    name: str = Field(min_length=1, max_length=20)
    years: int = Field(ge=0, le=80)


def main() -> None:
    ok = UserIn(name="hudi", years=30)
    print("通过:", ok)
    print("dict:", ok.model_dump())

    # 字符串 "1" 会被转成 int 1，这是 pydantic，不是普通注解
    coerced = UserIn(name="ada", years="1")  # type: ignore[arg-type]
    print("类型转换后 years =", coerced.years, type(coerced.years))

    try:
        UserIn(name="", years=-3)
    except ValidationError as e:
        print("校验失败条数:", len(e.errors()))
        for err in e.errors():
            print(" -", err["loc"], err["msg"])


if __name__ == "__main__":
    main()
