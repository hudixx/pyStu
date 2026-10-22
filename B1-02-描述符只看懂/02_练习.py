from __future__ import annotations


class NonBlank:
    def __set_name__(self, owner: object, name: str):
        self.public = name
        self.private = "_" + name
    def __get__(self, obj: object, objtype: type | None = None) -> object:
        if obj is None:
            return self
        return getattr(obj, self.private)
    def __set__(self, obj : object, value: str) -> None:
        if not value:
            raise ValueError("不能为空")
        setattr(obj, self.private, value)

class Person:
    name = NonBlank()

    def __init__(self, name: str) -> None:
        self.name = name

def main() -> None:
    print("类上", type(Person.name).__name__)
    person = Person("hudi")
    print("实例", person.name)
    try:
        Person("")
    except ValueError as e:
        print("拒绝", e)


if __name__ == "__main__":
    main()

# 题2不知道，请在参考答案的注释中个给出