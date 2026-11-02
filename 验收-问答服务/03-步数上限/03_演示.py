"""验收第 3 课：工具可以调用，但不能一直叫。

「列出」叫一次工具就回答。假模型若每次都还要工具，数到上限就停。
上限是 2。停下来的那一句是「步数到了」，不是再编一个答案。
"""

from __future__ import annotations

MAX_STEPS = 2


def run(kind: str) -> tuple[int, str]:
    """返回 (调用次数, 结果)。次数到了还在要工具，就停。"""

    tools = 0
    while tools < MAX_STEPS:
        tools += 1  # 这一轮模型要求调用工具。先记次数，再决定还叫不叫。
        if kind == "死循环":
            continue  # 假模型不给出最终回答，下一轮还要工具。
        return tools, "没有待办"  # 正常的一笔：工具结果已经够回答。
    return tools, "步数到了"


def main() -> None:
    calls, text = run("列出")
    print("列出", calls, text)
    calls, text = run("死循环")
    print("死循环", calls, text)


if __name__ == "__main__":
    main()
