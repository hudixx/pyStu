"""第 21 课示例：够用的 typing。运行时几乎看不出注解的效果，打印的是值。

对照 Java：
- list[str] / dict[str, int] ≈ List<String> / Map<String, Integer>
- Literal["user", "assistant"] ≈ 只有几个取值的枚举（运行时仍是 str）
- TypedDict ≈ 已知字段的 Map，取值仍用 ["key"]，不是 .field
- Protocol ≈ 不用 implements 的 interface
- type UserId = int ≈ 给检查器看的别名
"""

from __future__ import annotations

# Literal：注解里限定只能是这几个字符串。运行时还是普通 str。
# NotRequired：TypedDict 里这个键可以缺席。
# Protocol：结构化接口，不必显式继承。
# TypedDict：描述 dict 的键和值类型。
from typing import Literal, NotRequired, Protocol, TypedDict

# 3.12+ 的别名语法。UserId 在检查器眼里是「用户 id」，运行时就是 int。
type UserId = int
# 模型对话里的角色。拼错 "usr" 时 IDE / mypy 会划线，print 拦不住。
type Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    """一条聊天消息。对照一个只有字段、没有方法的 DTO，但运行时仍是 dict。

    必须有 role、content；name 可选。
    """

    role: Role
    content: str
    name: NotRequired[str]


class Closable(Protocol):
    """会 close 的东西。文件、Client、自己的连接都能算。运行时不强制继承本类。"""

    def close(self) -> None: ...


class FakeConn:
    """故意不写 class FakeConn(Closable)，演示 Protocol 按结构匹配。"""

    def close(self) -> None:
        print("FakeConn.close() 被调用")


def shutdown(resource: Closable) -> None:
    """只要求有 close 方法。对照 void shutdown(Closeable c)。"""
    resource.close()


def last_content(messages: list[ChatMessage]) -> str:
    """从消息列表取最后一条的 content。空列表返回空串。"""
    if not messages:
        return ""
    # TypedDict 取值仍是 ["content"]，没有 .content。
    return messages[-1]["content"]


def main() -> None:
    uid: UserId = 42
    print("UserId 运行时的类型 =", type(uid).__name__, "值 =", uid)

    messages: list[ChatMessage] = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好", "name": "hudi"},
    ]
    print("最后一条 =", last_content(messages))
    # 仍然是 dict，不是对象属性。
    print("第一条的键 =", list(messages[0].keys()))

    print("=== Protocol：不必继承 Closable ===")
    shutdown(FakeConn())


if __name__ == "__main__":
    main()
