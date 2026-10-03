from typing import Literal, TypedDict, Required, Protocol

Role = Literal["system", "user", "assistant"]
class ChatMessage(TypedDict):
    role: Required[Role]
    content: Required[str]

class Speaker(Protocol):
    def speak(self) -> str:...

class Dog:
    def speak(self) -> str:
        return "dog speak"
class Radio:
    def speak(self) -> str:
        return "radio speak"

def announce(speaker: Speaker) -> None:
    print(speaker.speak())


def only_user(messages: list[ChatMessage]) -> list[ChatMessage]:
    return [x for x in messages if x["role"] == "user"]

def main() -> None:

    msgs: list[ChatMessage] = [
        {"role": "system", "content": "你是系统"},
        {"role": "user", "content": "你是用户"},
        {"role": "assistant", "content": "你是助手"},
    ]
    users = only_user(msgs)
    print(users)

    announce(Dog())
    announce(Radio())

if __name__ == "__main__":
    main()

"""
题3对照题不知道，请在注释中给出简要答案
"""