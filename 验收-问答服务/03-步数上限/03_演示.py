"""验收第 3 课：工具可以调用，但不能一直叫。

「列出」叫一次工具就回答。假模型若每次都还要工具，数到上限就停。
上限是 2。停下来的那一句是「步数到了」，不是再编一个答案。
"""

from __future__ import annotations

# 全大写是约定，不是语言强制的常量。循环用它当次数上限。
MAX_STEPS = 2


def run(kind: str) -> tuple[int, str]:
    """返回 (调用次数, 结果)。次数到了还在要工具，就停。

    逻辑：
    1. tools 从 0 开始。只要还没到上限，就加 1，表示这一轮模型要求调用工具。
    2. kind 是「死循环」：不回答，continue 回到 while，再要一轮。
    3. 其他 kind（本课是「列出」）：立刻返回现在的次数和「没有待办」。正常路径只调用 1 次。
    4. while 因为 tools < MAX_STEPS 不再成立而结束：返回次数和「步数到了」。这是停，不是再编答案。
    返回元组。调用方用 calls, text = run(...) 拆开。对照一次 return 一个 Pair。
    """

    tools = 0
    while tools < MAX_STEPS:
        # while 先看条件。tools 到了 2 就不再进循环。对照 while (tools < MAX_STEPS)。
        tools += 1  # 这一轮模型要求调用工具。先记次数，再决定还叫不叫。
        if kind == "死循环":
            continue  # 假模型不给出最终回答，下一轮还要工具。
            # continue 不执行下面的 return。这一轮就这样结束，回到 while 再看次数。
        return tools, "没有待办"  # 正常的一笔：工具结果已经够回答。
        # return 后面两个值会收成一个元组。对照 return new Pair(tools, "没有待办")。
    return tools, "步数到了"  # 循环是因为次数用尽才退出的。死循环会走到这里，次数是 2。


def main() -> None:
    """先跑正常的「列出」，再跑停不下来的「死循环」，把次数和结果都打印出来。

    预期：列出是 1 和「没有待办」。死循环是 2 和「步数到了」。
    """

    calls, text = run("列出")  # 元组拆包。一个函数返回两个值，左边用逗号接。
    print("列出", calls, text)
    calls, text = run("死循环")  # 同名变量再赋值。上一轮的两个值被换掉。对照给局部变量重新赋值。
    print("死循环", calls, text)


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 工具可以调用，但循环次数要写在代码里。假模型若一轮轮还要工具，数到 MAX_STEPS 就停。
# 停下来的那一句是「步数到了」，不是再让模型编一个答案。
# 正常的「列出」只需要 1 次就 return。continue 才会把次数耗尽。
