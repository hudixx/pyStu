from __future__ import annotations

MAX_STEPS = 2


def run(kind: str) -> tuple[int, str]:

    tools = 0
    while tools < MAX_STEPS:
        tools += 1
        if kind == "死循环":
            continue
        return tools, "还有牛奶"
    return tools, "步数到了"


def main() -> None:
    calls, text = run("查库存")
    print("查库存", calls, text)
    calls, text = run("死循环")
    print("死循环", calls, text)


if __name__ == "__main__":
    main()
