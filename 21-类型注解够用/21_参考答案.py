"""第 21 课参考答案。TypedDict / Literal / Protocol 方向对，能跑通。

题 3：
- TypedDict：运行时仍是 dict，给 IDE / mypy 看键。取值 msg["content"]。
  适合「这就是一份 JSON，先让检查器帮忙」。
- pydantic BaseModel：构造时真校验、真转换，取值 msg.content。
  适合接口边界（第 17 课），对标 Jackson + Bean Validation。
- Java DTO：既有字段，又在编译期拦住类型。Python 没有 javac，
  所以 DTO 要拆成「检查器用的 TypedDict」和「运行时用的 pydantic」。
- msg["content"] 是 TypedDict；msg.content 是 BaseModel / 普通对象。
"""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict

# 3.12+ 也可以写成 type Role = Literal[...]，两种都行。
Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    """默认 total=True，两个字段都必填。不必再套 Required。"""

    role: Role
    content: str


def only_user(messages: list[ChatMessage]) -> list[ChatMessage]:
    """返回新列表，不要一边遍历一边 remove。

    Java 里 for (x : list) list.remove(x) 会 ConcurrentModificationException。
    Python 不会抛，但会跳过元素——本课数据碰巧能过，换个顺序就漏。
    """
    return [m for m in messages if m["role"] == "user"]


class Speaker(Protocol):
    """给检查器看的接口。实现方不必 class Dog(Speaker)。"""

    def speak(self) -> str: ...


class Dog:
    """故意不继承 Speaker。有 speak 就算数。"""

    def speak(self) -> str:
        return "汪"


class Radio:
    def speak(self) -> str:
        return "哔哔"


def announce(speaker: Speaker) -> None:
    """打印返回值。speak 自己不要 print。"""
    print(speaker.speak())


def main() -> None:
    msgs: list[ChatMessage] = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "hudi"},
        {"role": "assistant", "content": "你好"},
    ]
    print(only_user(msgs))
    announce(Dog())
    announce(Radio())


if __name__ == "__main__":
    main()
